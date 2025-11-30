import streamlit as st
from preprocessing import load_data, clean_cases, clean_hearings, merge_data
import pandas as pd
import utils

# ----------------------------
# Streamlit Config
# ----------------------------
st.set_page_config(
    page_title="Login - Nyayadrishti",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
body {
    background-color: #F8FAFC !important;
}

[data-testid="stContainer"] {
    padding-top: 50px;
}

.login-container {
    background: white;
    border-radius: 12px;
    padding: 40px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    max-width: 500px;
    margin: auto;
}

.login-title {
    text-align: center;
    color: #0F172A;
    font-size: 32px;
    font-weight: bold;
    margin-bottom: 10px;
}

.login-subtitle {
    text-align: center;
    color: #64748B;
    font-size: 16px;
    margin-bottom: 30px;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Initialize Session State
# ----------------------------
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.user_name = None

# ----------------------------
# Load Data (cached for performance)
# ----------------------------
@st.cache_resource
def load_all_data():
    cases, hearings = load_data()
    cases = clean_cases(cases)
    hearings = clean_hearings(hearings)
    merged = merge_data(cases, hearings)
    
    # Normalize column names
    cases.columns = cases.columns.str.strip().str.lower()
    hearings.columns = hearings.columns.str.strip().str.lower()
    merged.columns = merged.columns.str.strip().str.lower()
    
    return cases, hearings, merged

cases, hearings, merged = load_all_data()

# ----------------------------
# Login Page
# ----------------------------
from helpers.sidebar import render_sidebar
render_sidebar()

st.markdown("""
<div class="login-container">
    <div class="login-title">🔐 Nyayadrishti</div>
    <div class="login-subtitle">Judicial Case Management System</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

# Role Selection
role = st.radio(
    "Select your role:",
    ["Judge", "Advocate (Lawyer)"],
    horizontal=True,
    key="role_selection"
)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# Login Form
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    name = st.text_input("Enter your name:")
    
    if name:
        name_clean = name.strip().upper()
        passwords = utils.load_passwords()
        
        # Check if user is registered
        if name_clean not in passwords:
            st.info("👤 First-time login detected. Please register.")
            new_pass = st.text_input("Set Password:", type="password", key="reg_pass")
            confirm_pass = st.text_input("Confirm Password:", type="password", key="reg_confirm")
            if st.button("Register", key="btn_register"):
                if new_pass and new_pass == confirm_pass:
                    utils.register_judge(name_clean, new_pass)
                    st.success("✅ Registration successful. Please log in.")
                    st.rerun()
                else:
                    st.error("❌ Passwords do not match or empty.")
        else:
            # Existing user - show login form
            password = st.text_input("Enter Password:", type="password", key="login_pass")
            
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            
            col_login, col_forgot = st.columns(2)
            with col_login:
                if st.button("Login", use_container_width=True, type="primary", key="btn_login"):
                    if utils.validate_login(name_clean, password):
                        # Validate user exists in data
                        if role == "Judge":
                            judge_cases = merged[merged['beforehonourablejudges'].str.contains(name, case=False, na=False)] if 'beforehonourablejudges' in merged.columns else pd.DataFrame()
                            if judge_cases.empty:
                                judge_cases = merged[merged['judge'].str.upper() == name.upper()] if 'judge' in merged.columns else pd.DataFrame()
                            if judge_cases.empty:
                                st.error(f"❌ No cases found for Judge: {name}")
                            else:
                                st.session_state.authenticated = True
                                st.session_state.user_role = "Judge"
                                st.session_state.user_name = name
                                st.success(f"✅ Logged in as Judge: {name}")
                                st.switch_page("pages/Judge_Dashboard.py")
                        elif role == "Advocate (Lawyer)":
                            advocate_cases = merged[
                                merged['petitioneradvocate'].str.contains(name, case=False, na=False) |
                                merged['respondentadvocate'].str.contains(name, case=False, na=False)
                            ]
                            if advocate_cases.empty:
                                st.error(f"❌ No cases found for Advocate: {name}")
                            else:
                                st.session_state.authenticated = True
                                st.session_state.user_role = "Advocate"
                                st.session_state.user_name = name
                                st.success(f"✅ Logged in as Advocate: {name}")
                                st.switch_page("pages/Lawyer_Dashboard.py")
                    else:
                        st.error("❌ Incorrect password.")
            
            with col_forgot:
                if st.button("🔄 Reset Password", use_container_width=True, key="btn_reset_toggle"):
                    st.session_state.show_reset = True
            
            # Password reset form
            if st.session_state.get("show_reset", False):
                st.markdown("---")
                st.subheader("Reset Password")
                new_pass = st.text_input("Enter New Password:", type="password", key="reset_pass")
                confirm_pass = st.text_input("Confirm New Password:", type="password", key="reset_confirm")
                if st.button("Confirm Reset", key="btn_confirm_reset"):
                    if new_pass == confirm_pass and new_pass:
                        if utils.reset_password(name_clean, new_pass):
                            st.success("✅ Password reset successful.")
                            st.session_state.show_reset = False
                            st.rerun()
                        else:
                            st.error("❌ Error resetting password.")
                    else:
                        st.error("❌ Passwords do not match or empty.")

# ----------------------------
# Footer Info
# ----------------------------
st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center; color:#94A3B8; font-size:12px;'>
    <p>🔒 Default password format: First 4 letters of name (uppercase) + "01"</p>
    <p style='margin-top: 20px;'>© Law & Justice • Nyayadrishti</p>
</div>
""", unsafe_allow_html=True)
