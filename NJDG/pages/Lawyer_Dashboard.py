import streamlit as st
import pandas as pd
from utils import load_notes, save_notes, load_reminders, save_reminders
from preprocessing import load_data, clean_cases, clean_hearings, merge_data

# ----------------------------
# Streamlit Config
# ----------------------------
st.set_page_config(
    page_title="Advocate Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",  # SHOW SIDEBAR
)

from helpers.sidebar import render_sidebar
render_sidebar()

# ----------------------------
# Load & Preprocess Data
# ----------------------------
cases, hearings = load_data()
cases = clean_cases(cases)
hearings = clean_hearings(hearings)
merged = merge_data(cases, hearings)

# Normalize column names
cases.columns = cases.columns.str.strip().str.lower()
hearings.columns = hearings.columns.str.strip().str.lower()
merged.columns = merged.columns.str.strip().str.lower()

# ----------------------------
# Authentication Check
# ----------------------------
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("❌ Please login first")
    st.switch_page("pages/Login.py")
    st.stop()

if st.session_state.user_role != "Advocate":
    st.error("❌ Access Denied - This page is for Advocates only")
    st.info("Please login with an advocate account to access this dashboard.")
    if st.button("Return to Login", key="btn_return_login_advocate"):
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.session_state.user_name = None
        st.switch_page("pages/Login.py")
    st.stop()

lawyer_name = st.session_state.user_name

# ----------------------------
# Notes & Reminders Storage
# ----------------------------
notes = load_notes()          # dict {cnr_number: note_text}
reminders = load_reminders()  # dict {cnr_number: reminder_date}

# ----------------------------
# Load Advocate Portfolio
# ----------------------------
portfolio = merged[
    merged['petitioneradvocate'].str.contains(lawyer_name, case=False, na=False) |
    merged['respondentadvocate'].str.contains(lawyer_name, case=False, na=False)
]

if portfolio.empty:
    st.warning(f"No cases found for Advocate: {lawyer_name}")
    st.stop()

st.success(f"✅ Logged in as Advocate: *{lawyer_name}*")

# ----------------------------
# Main Dashboard Content
# ----------------------------
st.subheader("📂 Your Case Portfolio")
st.dataframe(portfolio[['cnr_number','case_number','case_type','current_status','date_filed','decision_date','nexthearingdate']])

# ----------------------------
# Case Search by CNR Number
# ----------------------------
cnr = st.text_input("Search Case by CNR Number:")
if cnr:
    if "cnr_number" not in portfolio.columns:
        st.error("❌ 'cnr_number' column not found in dataset.")
    else:
        df = portfolio[portfolio["cnr_number"] == cnr]
        if not df.empty:
            st.write(df)

            # ----------------------------
            # Personal Notes
            # ----------------------------
            st.subheader("📝 Personal Notes")
            text = st.text_area("Add Notes:", notes.get(cnr, ""))

            if st.button("Save Notes", key=f"save_notes_{cnr}"):
                notes[cnr] = text
                save_notes(notes)
                st.success("✅ Notes saved successfully!")

            # ----------------------------
            # Reminders
            # ----------------------------
            st.subheader("⏰ Set Reminder")
            reminder_date = st.date_input("Reminder Date:", pd.to_datetime(reminders.get(cnr, pd.to_datetime("today"))))
            if st.button("Save Reminder", key=f"save_reminder_{cnr}"):
                reminders[cnr] = str(reminder_date)
                save_reminders(reminders)
                st.success(f"✅ Reminder set for {reminder_date}")
        else:
            st.warning(f"No case found for CNR Number: {cnr}")

# ----------------------------
# Upcoming Reminders Overview
# ----------------------------
st.subheader("📅 Upcoming Reminders")
if reminders:
    reminder_df = pd.DataFrame(list(reminders.items()), columns=["CNR Number", "Reminder Date"])
    st.dataframe(reminder_df)
else:
    st.info("No reminders set yet.")
