import streamlit as st
import pandas as pd
from streamlit_cookies_manager import EncryptedCookieManager
from sessions import validate_token
from utils import load_notes, save_notes, load_reminders, save_reminders
from preprocessing import load_data, clean_cases, clean_hearings, merge_data
from helpers.sidebar import render_sidebar

st.set_page_config(
    page_title="Advocate Dashboard",
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
merged = merge_data(cases, hearings)

# Normalize column names
cases.columns = cases.columns.str.strip().str.lower()
hearings.columns = hearings.columns.str.strip().str.lower()
merged.columns = merged.columns.str.strip().str.lower()

# ----------------------------
# Notes & Reminders Storage
# ----------------------------
notes = load_notes()
reminders = load_reminders()


# ----------------------------
# Advocate Context (from session state)
# ----------------------------
lawyer_name = st.session_state.get("user_name", "").strip()
if not lawyer_name:
    st.error("Advocate name not found in session. Please log in again.")
    st.stop()

# Filter cases where lawyer appears as petitioner or respondent advocate
portfolio = merged[
    merged['petitioneradvocate'].str.contains(lawyer_name, case=False, na=False) |
    merged['respondentadvocate'].str.contains(lawyer_name, case=False, na=False)
]

if portfolio.empty:
    st.warning(f"No cases found for Advocate: {lawyer_name}")
    st.stop()

st.success(f"Logged in as *{lawyer_name}*")
# ----------------------------
# Case Portfolio Display
# ----------------------------
st.subheader("Your Case Portfolio")
st.dataframe(portfolio[['cnr_number','case_number','case_type','current_status','date_filed','decision_date','nexthearingdate']])

# ----------------------------
# Case Search by CNR Number
# ----------------------------
st.subheader("Search Case")
cnr = st.text_input("Search Case by CNR Number:")
if cnr:
    if "cnr_number" not in portfolio.columns:
        st.error("'cnr_number' column not found in dataset.")
    else:
        df = portfolio[portfolio["cnr_number"] == cnr]
        if not df.empty:
            st.write(df)

            # ----------------------------
            # Personal Notes
            # ----------------------------
            st.subheader("Personal Notes")
            text = st.text_area("Add Notes:", notes.get(cnr, ""))

            if st.button("Save Notes"):
                notes[cnr] = text
                save_notes(notes)
                st.success("Notes saved successfully!")

            # ----------------------------
            # Reminders
            # ----------------------------
            st.subheader("Set Reminder")
            reminder_date = st.date_input("Reminder Date:", pd.to_datetime(reminders.get(cnr, pd.to_datetime("today"))))
            if st.button("Save Reminder"):
                reminders[cnr] = str(reminder_date)
                save_reminders(reminders)
                st.success(f"Reminder set for {reminder_date}")
        else:
            st.warning(f"No case found for CNR Number: {cnr}")

# ----------------------------
# Upcoming Reminders Overview
# ----------------------------
st.subheader("Upcoming Reminders")
if reminders:
    reminder_df = pd.DataFrame(list(reminders.items()), columns=["CNR Number", "Reminder Date"])
    st.dataframe(reminder_df)
else:
    st.info("No reminders set yet.")
