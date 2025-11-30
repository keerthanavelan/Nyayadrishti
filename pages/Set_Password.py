import streamlit as st

st.set_page_config(
    page_title="Set Password - Nyayadrishti",
    layout="centered",
    initial_sidebar_state="expanded",
)

from auth import set_password, get_default_password
from helpers.sidebar import render_sidebar

render_sidebar()

# Check if user is logged in and on first login
if not st.session_state.get("authenticated") or not st.session_state.get("is_first_login"):
    st.warning(" Please log in first.")
    st.switch_page("pages/Login.py")

st.title("Set Your Password")
st.markdown("""
Welcome! This is your first login. Please set a strong password that you'll use for all future logins.
This password will be synchronized across all your devices.
""")

user_name = st.session_state.get("user_name", "")
st.info(f"Setting password for: **{user_name}**")

# Password input fields
new_password = st.text_input("New Password", type="password", placeholder="Enter a strong password")
confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")

if st.button("Set Password", use_container_width=True, type="primary"):
    
    if not new_password:
        st.error("Please enter a password.")
    elif not confirm_password:
        st.error("Please confirm your password.")
    elif len(new_password) < 6:
        st.error("Password must be at least 6 characters long.")
    elif new_password != confirm_password:
        st.error("Passwords do not match.")
    else:
        # Save the new password
        if set_password(user_name, new_password):
            st.success("Password set successfully!")
            st.balloons()
            
            # Clear the first-login flag
            st.session_state.is_first_login = False
            
            # Redirect to dashboard
            import time
            time.sleep(1)
            
            if st.session_state.user_role == "Judge":
                st.switch_page("pages/Judge_Dashboard.py")
            else:
                st.switch_page("pages/Lawyer_Dashboard.py")
        else:
            st.error("Failed to save password. Please try again.")

st.markdown("---")
st.markdown("""
**Password Requirements:**
- At least 6 characters long
- Can include letters, numbers, and special characters
""")