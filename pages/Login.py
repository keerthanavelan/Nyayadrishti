import streamlit as st
import warnings

from preprocessing import load_data, clean_cases, clean_hearings, merge_data
from auth import verify_password, set_password, is_first_login, get_default_password
from sessions import create_token, validate_token, get_token
import pandas as pd
import base64
from pathlib import Path
from helpers.sidebar import render_sidebar
from streamlit_cookies_manager import EncryptedCookieManager

# Cookie Setup (Persistent Login)
cookies = EncryptedCookieManager(
    prefix="nyayadrishti_",
    password="super_secret_password_here"   # change to anything private
)

if not cookies.ready():
    st.stop()   # Wait until cookies load

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="Login - Nyayadrishti",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------
# Global Custom CSS
# -------------------------------------------------
st.markdown("""<style>
body { background-color: #152035 !important; margin: 0; padding: 0; }
.brand-name { font-size: 48px; font-weight: 700; color: #F8FAFC; text-align:center; margin-top:150px; }
.brand-tagline { color:#94a3b8; text-align:center; }
.right-content { max-width:400px; width:100%; }
</style>""", unsafe_allow_html=True)

# -------------------------------------------------
# Auto-Login using Cookie
# -------------------------------------------------
def _should_auto_login(cookies_obj, grace_seconds=5):
    try:
        # ONLY check session token - do NOT fallback to 'authenticated' flag
        token = cookies_obj.get("session_token")
        name = cookies_obj.get("user_name")
        
        # Both token and name must be present
        if not token or not name:
            return False
        
        # Validate token against server
        if not validate_token(name, token):
            return False

        # If a logout marker exists and is recent, do NOT auto-login
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


# -------------------------------------------------
# Initialize session state defaults
# -------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.user_name = None

# -------------------------------------------------
# Load Data
# -------------------------------------------------
@st.cache_resource
def load_all_data():
    cases, hearings = load_data()
    cases = clean_cases(cases)
    hearings = clean_hearings(hearings)
    merged = merge_data(cases, hearings)

    cases.columns = cases.columns.str.strip().str.lower()
    hearings.columns = hearings.columns.str.strip().str.lower()
    merged.columns = merged.columns.str.strip().str.lower()
    return cases, hearings, merged

cases, hearings, merged = load_all_data()

# -------------------------------------------------
# Sidebar
# -------------------------------------------------
render_sidebar()

# -------------------------------------------------
# Debug toggle (visible on page) + auto-login
# -------------------------------------------------
if _should_auto_login(cookies):
    st.session_state.authenticated = True
    st.session_state.user_role = cookies.get("user_role")
    st.session_state.user_name = cookies.get("user_name")

    # AUTO REDIRECT
    if st.session_state.user_role == "Judge":
        st.switch_page("pages/Judge_Dashboard.py")
    elif st.session_state.user_role == "Advocate":
        st.switch_page("pages/Lawyer_Dashboard.py")

# -------------------------------------------------
# Layout
# -------------------------------------------------
left, right = st.columns([0.45, 0.55])

# LEFT
with left:
    st.markdown("<div class='brand-name'>Nyayadrishti</div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-tagline'>Justice Through Insight</div>", unsafe_allow_html=True)

# RIGHT
with right:
    st.markdown("<div class='right-content'>", unsafe_allow_html=True)

    role = st.radio("Login as", ["Judge", "Advocate (Lawyer)"], horizontal=True)
    name = st.text_input("USERNAME (UPPERCASE)", placeholder="Enter your name")
    password = st.text_input("PASSWORD", type="password", placeholder="Enter password")

    if st.button("Login", use_container_width=True):

        if not name:
            st.error("Please enter your name.")
        elif not password:
            st.error("Please enter your password.")
        else:
            if not verify_password(name, password, merged):
                st.error("Incorrect password.")
            else:
                if role == "Judge":
                    judge_cases = merged[
                        merged.get("beforehonourablejudges", pd.Series("", index=merged.index))
                        .str.contains(name, case=False, na=False)
                    ]
                    if judge_cases.empty:
                        st.error("No cases found for this Judge.")
                        st.stop()

                    st.session_state.user_role = "Judge"

                else:  # Advocate
                    advocate_cases = merged[
                        merged["petitioneradvocate"].str.contains(name, case=False, na=False) |
                        merged["respondentadvocate"].str.contains(name, case=False, na=False)
                    ]
                    if advocate_cases.empty:
                        st.error("No cases found for this Advocate.")
                        st.stop()

                    st.session_state.user_role = "Advocate"

                # Update login state
                st.session_state.authenticated = True
                st.session_state.user_name = name
                st.session_state.is_first_login = is_first_login(name)

                # -------------------------------------------------
                # SAVE TO COOKIES (PERSISTENT LOGIN)
                # -------------------------------------------------
                # Create server-side session token and store in cookie
                token = create_token(name)
                cookies["session_token"] = token
                cookies["authenticated"] = "true"
                cookies["user_role"] = st.session_state.user_role
                cookies["user_name"] = st.session_state.user_name
                cookies.save()

                # Redirect based on first-time login status
                if st.session_state.is_first_login:
                    st.switch_page("pages/Set_Password.py")
                else:
                    if st.session_state.user_role == "Judge":
                        st.switch_page("pages/Judge_Dashboard.py")
                    else:
                        st.switch_page("pages/Lawyer_Dashboard.py")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='margin-top:40px; text-align:center; color:#94A3B8; font-size:13px;'> 
    First time login: Password is first 4 letters of your name + 01
    </div>
    """, unsafe_allow_html=True)