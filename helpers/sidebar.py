import streamlit as st
from pathlib import Path
import base64
from streamlit_cookies_manager import EncryptedCookieManager

# Load logo
base_dir = Path(__file__).parent.parent
logo_path = base_dir / "logo.png"

logo_b64 = ""
if logo_path.exists():
    with open(logo_path, "rb") as f:
        logo_bytes = f.read()
    logo_b64 = base64.b64encode(logo_bytes).decode()

def render_sidebar():
    st.sidebar.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{
        background-color: #F8FAFC !important;
    }}

    [data-testid="stSidebar"] * {{
        color: black !important;
    }}

    /* Hide Streamlit's default page nav */
    [data-testid="stSidebar"] nav,
    [data-testid="stSidebarNav"],
    [data-testid="stVerticalNav"],
    nav[aria-label="Page navigation"] {{
        display: none !important;
    }}

    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton > button {{
        width: 100% !important;
        padding: 10px 14px !important;
        text-align: left !important;
        border-radius: 8px !important;
        background-color: transparent !important;
        color: black !important;
        font-weight: 500;
    }}

    [data-testid="stSidebar"] .stButton {{
        margin-bottom: 8px !important;
    }}
    [data-testid="stSidebar"] img {{
        position: fixed;  /* keep the logo in place while scrolling */
        top: 20px;
        left: 22px;
        width: 72px;
        z-index: 9999;
    }}

    </style>

    <!-- Top-left logo -->
    <img id="top-left-logo" src="data:image/png;base64,{logo_b64}">
    """, unsafe_allow_html=True)

    st.sidebar.header("Navigation")

    if st.sidebar.button("Home"):
        st.switch_page("app.py")

    # Show "Login" by default, but change to "Your Cases" if Judge is logged in
    if st.session_state.get("authenticated") and st.session_state.get("user_role") == "Judge":
        button_label = "Your Cases"
    elif st.session_state.get("authenticated") and st.session_state.get("user_role") == "Advocate (Lawyer)":
        button_label = "Your Cases"
    else:
        button_label = "Login"

    if st.sidebar.button(button_label):
        if st.session_state.get("authenticated"):
            if st.session_state.user_role == "Judge":
                st.switch_page("pages/Judge_Dashboard.py")
            elif st.session_state.user_role == "Advocate":
                st.switch_page("pages/Lawyer_Dashboard.py")
            else:
                st.switch_page("pages/Login.py")
        else:
            st.switch_page("pages/Login.py")

    if st.sidebar.button("AI Predictions"):
        st.switch_page("pages/AI_Predictions.py")

    if st.sidebar.button("Anomaly Detection"):
        st.switch_page("pages/Anomaly_Detection.py")

    if st.sidebar.button("Analytics"):
        st.switch_page("pages/Analytics.py")

    st.sidebar.markdown("---")

    if st.session_state.get("authenticated"):
        if st.sidebar.button("Logout"):
            # Revoke server-side session token first (use current user_name)
            try:
                from sessions import delete_token
                current_user = st.session_state.get("user_name")
                print(f"[LOGOUT] Attempting to revoke token for user: {current_user}")
                if current_user:
                    delete_token(current_user)
                    print(f"[LOGOUT] Token revoked successfully for {current_user}")
                else:
                    print(f"[LOGOUT] No user_name in session_state")
            except Exception as e:
                print(f"[LOGOUT] Error revoking token: {e}")
                pass

            # Clear session state
            st.session_state.authenticated = False
            st.session_state.user_role = None
            st.session_state.user_name = None

            # Clear cookies (if available) by deleting keys so they don't auto-login
            try:
                cookies = EncryptedCookieManager(
                    prefix="nyayadrishti_",
                    password="super_secret_password_here"
                )
                if cookies.ready():
                    # Remove keys if present
                    try:
                        if cookies.get("authenticated") is not None:
                            del cookies["authenticated"]
                        if cookies.get("user_role") is not None:
                            del cookies["user_role"]
                        if cookies.get("user_name") is not None:
                            del cookies["user_name"]
                    except Exception:
                        # Fallback: set to false/empty then save
                        cookies["authenticated"] = "false"
                        cookies["user_role"] = ""
                        cookies["user_name"] = ""

                    # Also set a logout marker timestamp so clients that still have
                    # `authenticated` won't auto-login immediately after logout.
                    import time
                    try:
                        cookies["logged_out"] = str(time.time())
                    except Exception:
                        # if inserting fails, ignore (we already cleared keys)
                        pass

                    cookies.save()
            except Exception:
                # If cookie manager isn't available for some reason, continue
                pass

            # Redirect to login page
            st.switch_page("pages/Login.py")