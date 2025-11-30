import os
import sys
import io
import streamlit as st
from preprocessing import load_data, clean_cases, clean_hearings, merge_data
import base64
from pathlib import Path
import warnings

# Suppress all deprecation and cache warnings
os.environ['STREAMLIT_LOGGER_LEVEL'] = 'error'
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*st.cache.*")
warnings.filterwarnings("ignore", category=FutureWarning)

# Redirect stderr to suppress Streamlit's internal warning messages
class WarningFilter(io.StringIO):
    def write(self, message):
        if "st.cache" not in message and "deprecated" not in message.lower():
            return super().write(message)
        return len(message)

# Store original stderr
_original_stderr = sys.stderr

# -------------------------------------------------
# LOAD LOGO
# -------------------------------------------------
base_dir = Path(__file__).parent
logo_path = base_dir / "logo.png"

with open(logo_path, "rb") as f:
    logo_bytes = f.read()

logo_b64 = base64.b64encode(logo_bytes).decode()
# -------------------------------------------------
# PAGE CONFIG — FULL WIDTH + SIDEBAR HIDDEN
# -------------------------------------------------
st.set_page_config(
    page_title="Nyayadrishti",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon=logo_path
)

# -------------------------------------------------
# GLOBAL STYLING
# -------------------------------------------------
st.markdown(f"""
<style>

/* Remove default Streamlit top padding */
header[data-testid="stHeader"] {{
    background: none !important;
    height: 0px !important;
}}

/* Hide Streamlit sidebar COMPLETELY */
[data-testid="stSidebar"], [data-testid="stSidebarNav"] {{
    display: none !important;
}}
 
/* Make page background clean */
.stApp {{
    background-color: #F8FAFC !important;
    padding-top: 0 !important;
}}

/* Top-left logo */
#top-left-logo {{
    position: fixed;  /* keep the logo in place while scrolling */
    top: 20px;
    left: 22px;
    width: 72px;
    z-index: 9999;
}}

/* Login button style */
[data-testid="stButton"] button {{
    background-color: #0F172A !important;
    color: #F8FAFC !important;         /* text color */
    border-radius: 8px !important;
    padding: 8px 18px !important;
    border: 1px solid #1E293B !important;
}}

[data-testid="stButton"] button:hover {{
    background-color: #1B2A41 !important;
    color: white !important;
}}

/* Feature Cards */
.feature-card {{
    background: #152035;
    border-radius: 16px;
    padding: 28px;
    border: 1px solid #0F172A;
    height: 200px;

    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;

    color: #F5E6C8 !important;
    text-align: center;
    font-family: 'Inter', sans-serif;

    transition: 0.2s;
}}

.feature-card:hover {{
    background: #1C2A42;
    cursor: pointer;
}}

/* Feature Title */
.feature-title {{
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 8px;
    color: #F8FAFC !important;
}}

/* Feature Description */
.feature-desc {{
    font-size: 15px;
    color: #F1F5F9 !important;
}}

/* Remove underline from links */
a {{
    text-decoration: none !important;
}}

/* Stats cards */
.stat-card {{
    background: white;
    border-radius: 14px;
    padding: 22px;
    border: 1px solid #E2E8F0;
    text-align:center;
}}

.stat-title {{
    color:#64748B;
    font-size:14px;
}}

.stat-value {{
    color:#0F172A;
    font-size:22px;
    font-weight:bold;
}}

</style>

<!-- Top-left logo -->
<img id="top-left-logo" src="data:image/png;base64,{logo_b64}">
""", unsafe_allow_html=True)

# -------------------------------------------------
# LOGIN BUTTON (top-right)
# -------------------------------------------------
col1, col2 = st.columns([0.92, 0.08])
with col2:
    if st.button("Login", key="login"):
        st.switch_page("pages/Login.py")

# -------------------------------------------------
# HERO SECTION
# -------------------------------------------------
st.markdown("""
<h1 style='text-align:center; color:#0F172A; font-size:46px;'>
    Nyayadrishti
</h1>

<h3 style='text-align:center; color:#334155; margin-top:-12px; font-size:22px;'>
    Judicial Case Management Dashboard
</h3>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)

st.markdown("""
<div style='
    text-align:center;
    font-size:18px;
    max-width: 900px;
    margin:auto;
    color:#475569;
    line-height:1.5;
'>
For faster case disposal, effective monitoring, and transparent access to case insights.
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------
# LOAD DATA (Statistics)
# -------------------------------------------------
cases, hearings = load_data()
cases = clean_cases(cases)
hearings = clean_hearings(hearings)

merged = merge_data(cases, hearings)

total_cases = len(cases)
civil_cases = len(cases)
criminal_cases = 0
older_than_1 = len(cases[cases.get("disposal_days", 0) > 365])

# -------------------------------------------------
# QUICK STATS
# -------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class='stat-card'>
        <div class='stat-title'>Total Cases</div>
        <div class='stat-value'>{total_cases:,}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class='stat-card'>
        <div class='stat-title'>Civil Cases</div>
        <div class='stat-value'>{civil_cases:,}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class='stat-card'>
        <div class='stat-title'>Criminal Cases</div>
        <div class='stat-value'>{criminal_cases:,}</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class='stat-card'>
        <div class='stat-title'>Pending > 1 year</div>
        <div class='stat-value'>{older_than_1:,}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------
# CARD GENERATOR
# -------------------------------------------------
def card(title, desc, page):
    return f"""
    <a href="/{page}" target="_self">
        <div class="feature-card">
            <div class="feature-title">{title}</div>
            <div class="feature-desc">{desc}</div>
        </div>
    </a>
    """

# -------------------------------------------------
# MAIN CARDS 
# -------------------------------------------------
row = st.columns(3)

with row[0]:
    st.markdown(card("Analytics Dashboard",
                     "Visual insights across cases, timelines, judges.",
                     "Analytics"),
                unsafe_allow_html=True)

with row[1]:
    st.markdown(card("AI Predictions",
                     "Forecast hearings, delays, disposal patterns.",
                     "AI_Predictions"),
                unsafe_allow_html=True)

with row[2]:
    st.markdown(card("Anomaly Detection",
                     "Identify unusual case durations & patterns.",
                     "Anomaly_Detection"),
                unsafe_allow_html=True)

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("""
<div style='margin-top:80px; text-align:center; color:#94A3B8; font-size:13px;'> 
• Law & Justice • Developed by Nyayadrishti •
</div>
""", unsafe_allow_html=True)
