import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_cookies_manager import EncryptedCookieManager
from preprocessing import load_data, clean_cases, clean_hearings
from helpers.sidebar import render_sidebar
from sessions import validate_token

st.set_page_config(
    page_title="Judge Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Cookie Setup (Persistent Login)
cookies = EncryptedCookieManager(
    prefix="nyayadrishti_",
    password="super_secret_password_here"
)

if not cookies.ready():
    st.stop()


def _should_auto_login(cookies_obj, grace_seconds=5):
    try:
        # ONLY check session token - do NOT fallback to 'authenticated' flag
        token = cookies_obj.get("session_token")
        name = cookies_obj.get("user_name")
        
        if not token or not name:
            return False
        
        if not validate_token(name, token):
            return False

        logged_out = cookies_obj.get("logged_out")
        if logged_out:
            try:
                import time
                ts = float(logged_out)
                if time.time() - ts < grace_seconds:
                    return False
            except Exception:
                return False

        return True
    except Exception:
        return False


# Restore login from cookies if valid session token and not already authenticated
if not st.session_state.get("authenticated") and _should_auto_login(cookies):
    st.session_state.authenticated = True
    st.session_state.user_role = cookies.get("user_role")
    st.session_state.user_name = cookies.get("user_name")

# Check authentication - allow if either session state is set OR valid cookie token exists
if not st.session_state.get("authenticated") and not _should_auto_login(cookies):
    st.warning("Please log in first.")
    st.switch_page("pages/Login.py")

# Check if first login - redirect to password setup
if st.session_state.get("is_first_login"):
    st.switch_page("pages/Set_Password.py")
    
render_sidebar()

# Load & Preprocess Data
cases, hearings = load_data()
cases = clean_cases(cases)
hearings = clean_hearings(hearings)

# Normalize column names
cases.columns = cases.columns.str.strip().str.lower()
hearings.columns = hearings.columns.str.strip().str.lower()

# ----------------------------
# Merge Cases & Hearings
# ----------------------------
case_keys = ['combined_case_number', 'cnr_number', 'case_number']
hearing_keys = ['combinedcasenumber', 'cnr_number', 'case_number']

left_key = next((k for k in case_keys if k in cases.columns), None)
right_key = next((k for k in hearing_keys if k in hearings.columns), None)

if not left_key or not right_key:
    st.error("Could not find valid merge key.")
    st.stop()

merged = pd.merge(
    cases,
    hearings,
    left_on=left_key,
    right_on=right_key,
    how='left',
    suffixes=('_case', '_hear')
)

merged['judge'] = merged.get('beforehonourablejudges', merged.get('njdg_judge_name', 'unknown'))

# ----------------------------
# Judge Context
# ----------------------------
judge_name = st.session_state.get("user_name", "").strip()
if not judge_name:
    st.error("Judge name not found in session. Please log in again.")
    st.stop()

judge_cases = merged[merged['judge'].str.upper() == judge_name.upper()]
if judge_cases.empty:
    st.warning(f"No cases found for Judge: {judge_name}")
    st.stop()

st.success(f"Logged in as *{judge_name}*")


# ----------------------------
# Top Navigation (horizontal)
# ----------------------------
st.markdown("<h3 style='margin-top: -10px;'>Navigation</h3>", unsafe_allow_html=True)

page = st.pills(
    "",
    ["Case Management", "Alerts", "Hearing Overview", "Dashboards / Charts"],
    selection_mode="single",
    label_visibility="collapsed"
)

# ----------------------------
# PAGE 1 — CASE MANAGEMENT
# ----------------------------
if page == "Case Management":
    st.header("Case Management")

    status_filter = st.multiselect(
        "Filter by case status:",
        judge_cases['current_status'].dropna().unique(),
        default=judge_cases['current_status'].dropna().unique()
    )
    filtered_cases = judge_cases[judge_cases['current_status'].isin(status_filter)]

    st.dataframe(filtered_cases[
        ['case_number', 'current_status', 'date_filed', 'decision_date',
         'nature_of_disposal', 'disposaltime_adj']
    ])

# ----------------------------
# PAGE 2 — ALERTS
# ----------------------------
elif page == "Alerts":
    st.header("Alerts")

    today = pd.to_datetime("today").normalize()
    judge_cases['age_days'] = (today - pd.to_datetime(judge_cases['date_filed'], errors='coerce')).dt.days

    st.subheader("Aging Cases (>365 days)")
    aging = judge_cases[judge_cases['age_days'] > 365]
    if not aging.empty:
        st.dataframe(aging[['case_number', 'current_status', 'date_filed', 'age_days', 'disposaltime_adj']])
    else:
        st.info("No aging cases found")

    st.subheader("Pending Cases")
    pending = judge_cases[judge_cases['current_status'].str.lower() != 'disposed']
    if not pending.empty:
        st.dataframe(pending[['case_number', 'current_status', 'date_filed', 'disposaltime_adj']])
    else:
        st.info("No pending cases found")

# ----------------------------
# PAGE 3 — HEARING OVERVIEW
# ----------------------------
elif page == "Hearing Overview":
    st.header("Hearing Overview")

    today = pd.to_datetime("today").normalize()

    if 'nexthearingdate' in judge_cases.columns:
        judge_cases['nexthearingdate'] = pd.to_datetime(judge_cases['nexthearingdate'], errors='coerce')
        today_hearings = judge_cases[judge_cases['nexthearingdate'] == today]
        upcoming_hearings = judge_cases[judge_cases['nexthearingdate'] > today]
    else:
        today_hearings, upcoming_hearings = pd.DataFrame(), pd.DataFrame()

    rescheduled = judge_cases[judge_cases['previoushearing'].notnull()] if 'previoushearing' in judge_cases.columns else pd.DataFrame()

    st.subheader("Today's Hearings")
    if not today_hearings.empty:
        st.dataframe(today_hearings[['case_number', 'nexthearingdate', 'appearancedate', 'purposeofhearing', 'judge']])
    else:
        st.info("No hearings today")

    st.subheader("Upcoming Hearings")
    if not upcoming_hearings.empty:
        st.dataframe(upcoming_hearings[['case_number', 'nexthearingdate', 'appearancedate', 'purposeofhearing', 'judge']])
    else:
        st.info("No upcoming hearings")

    st.subheader("Rescheduled Hearings")
    if not rescheduled.empty:
        st.dataframe(rescheduled[['case_number', 'nexthearingdate', 'previoushearing', 'purposeofhearing']])
    else:
        st.info("No rescheduled hearings")

# ----------------------------
# PAGE 4 — DASHBOARDS / CHARTS
# ----------------------------
elif page == "Dashboards / Charts":
    st.header("Dashboards & Charts")

    if 'disposal_year' in judge_cases.columns:
        disposal_trend = judge_cases.groupby('disposal_year').size().reset_index(name='count')
        fig = px.line(disposal_trend, x='disposal_year', y='count', title="Case Disposal Trend")
        st.plotly_chart(fig, width='stretch')

    fig_status = px.bar(
        judge_cases.groupby('current_status').size().reset_index(name='count'),
        x='current_status',
        y='count',
        title="Case Status Distribution"
    )
    st.plotly_chart(fig_status, width='stretch')
