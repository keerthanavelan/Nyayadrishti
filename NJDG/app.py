import streamlit as st
from preprocessing import load_data, clean_cases, clean_hearings, merge_data

# --------------------------------------------
# PAGE CONFIG — HIDE SIDEBAR ON HOME PAGE
# --------------------------------------------
st.set_page_config(
    page_title="Nyayadrishti",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import base64
from PIL import Image
import streamlit as st

from pathlib import Path

base_dir = Path(__file__).parent

'''cases_path = base_dir / "data" / "ISDMHack_Cases_students.csv"
hearings_path = base_dir / "data" / "ISDMHack_Hear_students.csv"'''

logo_path = base_dir / "logo.png"

# Load image and convert to base64 safely
with open(logo_path, "rb") as f:
    logo_bytes = f.read()
logo_b64 = base64.b64encode(logo_bytes).decode()

st.markdown(f"""
<style>
#top-left-logo {{
    position: fixed;
    top: 18px;
    left: 22px;
    width: 70px;
    z-index: 9999;
}}

#top-right-login {{
    position: fixed;
    top: 20px;
    right: 22px;
    z-index: 9999;
}}

[data-testid="stButton"] button[key="top_login"]:hover {{
    color: #F5E6C8 !important;
    background-color: #22344F !important;
}}

[data-testid="stButton"] button:hover {{
    color: #F5E6C8 !important;
    background-color: #22344F !important;
}}

button:hover {{
    color: #1B2A41 !important;
}}
</style>

<img id="top-left-logo" src="data:image/jpeg;base64,{logo_b64}">
""", unsafe_allow_html=True)

# Login button in top right
col1, col2 = st.columns([0.85, 0.15])
with col2:
    if st.button("🔐 Login", key="top_login", use_container_width=True):
        st.switch_page("pages/Login.py")

from helpers.sidebar import render_sidebar
render_sidebar()


# --------------------------------------------
# GLOBAL WHITE BACKGROUND + CLEAN UI
# --------------------------------------------
st.markdown("""
<style>

.stApp {
    background-color: #F8FAFC !important;   /* Light neutral background */
    padding-top: 0 !important;
}

/* Remove default Streamlit top spacing */
header[data-testid="stHeader"] {
    background: none !important;
    height: 0px !important;
}

/* Sidebar visible (but hide Streamlit built-in page navigation) */
[data-testid="stSidebar"] {
    display: block !important;
}

/* Hide Streamlit's default pages navigation inside the sidebar so only
   our custom buttons appear */
[data-testid="stSidebar"] nav,
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* --------- CARD STYLES ---------- */
.feature-card {
    background: #1B2A41;        /* Softer navy */
    border-radius: 14px;
    padding: 28px;
    border: 1px solid #1E293B;
    color: #F5E6C8 !important;  /* Beige text */
    font-family: 'Inter', sans-serif;
            
    display: flex;                 /* ENABLE FLEX */
    flex-direction: column;        /* STACK title + text */
    justify-content: center;       /* VERTICAL CENTER */
    align-items: center;           /* HORIZONTAL CENTER */
            
    height: 200px;
    text-align: center;
}

.feature-card:hover {
    background: #22344F;
    cursor: pointer;
}

.feature-title {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 6px;
    color: #F8FAFC !important;
}

.feature-desc {
    font-size: 15px;
    color: #F8FAFC !important;
}

a {
    text-decoration: none !important;
}

/* --------- STATS BOXES ---------- */

.stat-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #e2e8f0;
    text-align:center;
    font-family:'Inter', sans-serif;
}
.stat-title {
    color:#64748b;
    font-size:14px;
}
.stat-value {
    color:#0F172A;
    font-size:22px;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------
# TITLE + HERO SECTION
# --------------------------------------------
st.markdown("""
<h1 style='text-align:center; color:#0F172A; font-size:46px; margin-top:0;'>
    Nyayadrishti
</h1>

<h3 style='text-align:center; color:#334155; margin-top:-10px; font-size:22px;'>
    Judicial Case Management Dashboard
</h3>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

# Intro paragraph
st.markdown("""
<div style="
    text-align:center;
    font-size:18px;
    max-width: 900px;
    margin:auto;
    color:#475569;
    line-height:1.5;
">
For faster case disposal, effective monitoring, and transparent access to case insights
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)


# --------------------------------------------
# LOAD DATA (for statistics)
# --------------------------------------------
cases, hearings = load_data()
cases = clean_cases(cases)
hearings = clean_hearings(hearings)
merged = merge_data(cases, hearings)

total_cases = len(cases)
civil_cases = len(cases)  # dataset only has civil for now
criminal_cases = 0        # empty now, but future ready

older_than_1 = len(cases[cases.get("disposal_days", 0) > 365])


# --------------------------------------------
# QUICK STATS ROW (4 BOXES)
# --------------------------------------------
s1, s2, s3, s4 = st.columns(4)

with s1:
    st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-title'>Total Cases</div>
            <div class='stat-value'>{total_cases:,}</div>
        </div>
    """, unsafe_allow_html=True)

with s2:
    st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-title'>Civil Cases</div>
            <div class='stat-value'>{civil_cases:,}</div>
        </div>
    """, unsafe_allow_html=True)

with s3:
    st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-title'>Criminal Cases</div>
            <div class='stat-value'>{criminal_cases:,}</div>
        </div>
    """, unsafe_allow_html=True)

with s4:
    st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-title'>Pending > 1 year</div>
            <div class='stat-value'>{older_than_1:,}</div>
        </div>
    """, unsafe_allow_html=True)


st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)


# --------------------------------------------
# CARD GENERATOR FUNCTION
# --------------------------------------------
def card(title, desc, page):
    return f"""
    <a href="/{page}" target="_self">
        <div class="feature-card">
            <div class="feature-title">{title}</div>
            <div class="feature-desc">{desc}</div>
        </div>
    </a>
    """


# --------------------------------------------
# CARDS — ROW 1
# --------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(card(
        "Analytics Dashboard",
        "Visual insights across cases, timelines, judges",
        "Analytics"
    ), unsafe_allow_html=True)

with col2:
    st.markdown(card(
        "Judge Dashboard",
        "Judge caseload overview and case status",
        "Login"
    ), unsafe_allow_html=True)

with col3:
    st.markdown(card(
        "Advocate Workspace",
        "Track hearings, clients, and case updates",
        "Login"
    ), unsafe_allow_html=True)


# add spacing between rows
st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)


# --------------------------------------------
# CARDS — ROW 2
# --------------------------------------------
col4, col5, col6 = st.columns(3)

with col4:
    st.markdown(card(
        "AI Predictions",
        "Forecast hearings, delays, disposal patterns",
        "AI_Predictions"
    ), unsafe_allow_html=True)

with col5:
    st.markdown(card(
        "Anomaly Detection",
        "Identify unusual case durations or patterns",
        "Anomaly_Detection"
    ), unsafe_allow_html=True)

with col6:
    st.markdown(card(
        "Cause List Generator",
        "Generate daily cause lists intelligently",
        "Cause_List"
    ), unsafe_allow_html=True)


# --------------------------------------------
# FOOTER
# --------------------------------------------
st.markdown("""
<div style='margin-top:80px; text-align:center; color:#94A3B8; font-size:13px;'> 
            • Law & Justice • Developed by Nyayadrishti • </div>
""", unsafe_allow_html=True)
