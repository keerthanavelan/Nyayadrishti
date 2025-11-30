import streamlit as st


def render_sidebar():
    """Render a consistent sidebar used across all pages.
    This includes navigation buttons and logout handling.
    Calling this function will render the sidebar and handle page switches.
    """
    # Styling for sidebar and hide Streamlit's built-in page nav
    st.sidebar.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #1B2A41 !important;
    }

    [data-testid="stSidebar"] * {
        color: F8FAFC !important;
    }

    /* Hide Streamlit's default pages/navigation block so only our
       custom buttons appear in the sidebar */
    [data-testid="stSidebar"] nav,
    [data-testid="stSidebarNav"],
    [data-testid="stVerticalNav"],
    nav[aria-label="Page navigation"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
        overflow: hidden !important;
    }

        /* Make all sidebar buttons equal width and consistent spacing/padding */
        [data-testid="stSidebar"] .stButton > button {
            width: 100% !important;
            box-sizing: border-box !important;
            padding: 10px 14px !important;
            text-align: left !important;
            border-radius: 8px !important;
            background-color: transparent !important;
        }

        [data-testid="stSidebar"] .stButton {
            margin-bottom: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.header("Navigation")

    # Dashboard button: route by role
    if st.sidebar.button("Home"):
        st.switch_page("app.py")

    if st.sidebar.button("Dashboard"):
        if 'authenticated' in st.session_state and st.session_state.authenticated:
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

    # Logout handling (visible only when authenticated)
    if 'authenticated' in st.session_state and st.session_state.authenticated:
        if st.sidebar.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user_role = None
            st.session_state.user_name = None
            st.switch_page("pages/Login.py")
