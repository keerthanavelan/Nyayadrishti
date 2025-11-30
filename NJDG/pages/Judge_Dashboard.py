import streamlit as st
import pandas as pd
import plotly.express as px
from preprocessing import load_data, clean_cases, clean_hearings

# ----------------------------
# Streamlit Config
# ----------------------------
st.set_page_config(
    page_title="Judge Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

from helpers.sidebar import render_sidebar
render_sidebar()

# ----------------------------
# Authentication Check
# ----------------------------
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("❌ Please login first")
    st.switch_page("pages/Login.py")
    st.stop()

if st.session_state.user_role != "Judge":
    st.error("❌ Access Denied - This page is for Judges only")
    st.info("Please login with a judge account to access this dashboard.")
    if st.button("Return to Login", key="btn_return_login_judge"):
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.session_state.user_name = None
        st.switch_page("pages/Login.py")
    st.stop()

judge_name = st.session_state.user_name

# ----------------------------
# Load & Preprocess Data
# ----------------------------
cases, hearings = load_data()
cases = clean_cases(cases)
hearings = clean_hearings(hearings)

cases.columns = cases.columns.str.strip().str.lower()
hearings.columns = hearings.columns.str.strip().str.lower()

# Safe merge
case_keys = ['combined_case_number', 'cnr_number', 'case_number']
hearing_keys = ['combinedcasenumber', 'cnr_number', 'case_number']
left_key = next((k for k in case_keys if k in cases.columns), None)
right_key = next((k for k in hearing_keys if k in hearings.columns), None)

if not left_key or not right_key:
    st.error("❌ Could not find valid merge key.")
    st.stop()

merged = pd.merge(
    cases,
    hearings,
    left_on=left_key,
    right_on=right_key,
    how='left',
    suffixes=('_case', '_hear')
)

# Judge column handling
if 'beforehonourablejudges' in merged.columns and merged['beforehonourablejudges'].notna().any():
    merged['judge'] = merged['beforehonourablejudges']
elif 'njdg_judge_name' in merged.columns:
    merged['judge'] = merged['njdg_judge_name']
else:
    merged['judge'] = 'unknown'

# Normalize judge names
merged['judge'] = merged['judge'].astype(str).str.strip().str.upper()

# Get judge cases
judge_cases = merged[merged['judge'] == judge_name.upper()]

if judge_cases.empty:
    st.warning(f"No cases found for Judge: {judge_name}")
    st.stop()

st.success(f"✅ Logged in as *{judge_name}*")

# ----------------------------
# Internal page navigation
# ----------------------------
page = st.radio(
    "Go to:",
    ["Case Management", "Alerts", "Hearing Overview", "Dashboards / Charts", "Notes & Reminders"],
    key="judge_page_nav"
)

# ----------------------------
# Case Management
# ----------------------------
if page == "Case Management":
    st.header("📋 Case Management")
    status_filter = st.multiselect(
        "Filter by case status:",
        judge_cases['current_status'].dropna().unique(),
        default=judge_cases['current_status'].dropna().unique()
    )
    filtered = judge_cases[judge_cases['current_status'].isin(status_filter)]
    st.dataframe(filtered[['case_number', 'current_status', 'date_filed', 'decision_date', 'nature_of_disposal', 'disposaltime_adj']])

# ----------------------------
# Alerts
# ----------------------------
elif page == "Alerts":
    st.header("⚠ Alerts")
    today = pd.to_datetime("today").normalize()
    judge_cases['age_days'] = (today - pd.to_datetime(judge_cases['date_filed'], errors='coerce')).dt.days

    st.subheader("📌 Aging Cases (>365 days)")
    aging = judge_cases[judge_cases['age_days'] > 365]
    if not aging.empty:
        st.dataframe(aging[['case_number', 'current_status', 'date_filed', 'age_days', 'disposaltime_adj']])
    else:
        st.info("No aging cases")

    st.subheader("📌 Pending Cases")
    pending = judge_cases[judge_cases['current_status'].str.lower() != 'disposed']
    if not pending.empty:
        st.dataframe(pending[['case_number', 'current_status', 'date_filed', 'disposaltime_adj']])
    else:
        st.info("No pending cases")

# ----------------------------
# Hearing Overview
# ----------------------------
elif page == "Hearing Overview":
    st.header("🎤 Hearing Overview")
    today = pd.to_datetime("today").normalize()

    if 'nexthearingdate' in judge_cases.columns:
        judge_cases['nexthearingdate'] = pd.to_datetime(judge_cases['nexthearingdate'], errors='coerce')
        today_hearings = judge_cases[judge_cases['nexthearingdate'] == today]
        upcoming = judge_cases[judge_cases['nexthearingdate'] > today]
    else:
        today_hearings, upcoming = pd.DataFrame(), pd.DataFrame()

    rescheduled = judge_cases[judge_cases['previoushearing'].notnull()] if 'previoushearing' in judge_cases.columns else pd.DataFrame()

    st.subheader("📅 Today's Hearings")
    if not today_hearings.empty:
        st.dataframe(today_hearings[['case_number', 'nexthearingdate', 'appearancedate', 'purposeofhearing', 'judge']])
    else:
        st.info("No hearings today")

    st.subheader("📅 Upcoming Hearings")
    if not upcoming.empty:
        st.dataframe(upcoming[['case_number', 'nexthearingdate', 'appearancedate', 'purposeofhearing', 'judge']])
    else:
        st.info("No upcoming hearings")

    st.subheader("📅 Rescheduled Hearings")
    if not rescheduled.empty:
        st.dataframe(rescheduled[['case_number', 'nexthearingdate', 'previoushearing', 'purposeofhearing']])
    else:
        st.info("No rescheduled hearings")

# ----------------------------
# Dashboards / Charts
# ----------------------------
elif page == "Dashboards / Charts":
    st.header("📊 Dashboards & Charts")
    
    # Trend chart
    if 'disposal_year' in judge_cases.columns:
        disposal_trend = judge_cases.groupby('disposal_year').size().reset_index(name='count')
        fig = px.line(disposal_trend, x='disposal_year', y='count', title="Case Disposal Trend")
        st.plotly_chart(fig, use_container_width=True)

    # Status Distribution
    fig_status = px.bar(
        judge_cases.groupby('current_status').size().reset_index(name='count'),
        x='current_status',
        y='count',
        title="Case Status Distribution"
    )
    st.plotly_chart(fig_status, use_container_width=True)

# ----------------------------
# Notes & Reminders
# ----------------------------
elif page == "Notes & Reminders":
    st.header("📝 Notes & Reminders")
    st.info("Notes and reminders feature coming soon!")
