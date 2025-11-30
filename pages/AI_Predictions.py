import streamlit as st
import pandas as pd
from preprocessing import load_data, clean_cases
from helpers.sidebar import render_sidebar

st.set_page_config(
    page_title="AI Predictions",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #F8FAFC !important;
}

[data-testid="stSidebar"] * {
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

render_sidebar()

st.title("AI predictions")

# Load and clean data
cases, hearings = load_data()
cases = clean_cases(cases)

required_cols = ["cnr_number", "disposal_days", "total_hearings", "filing_year"]
missing = [col for col in required_cols if col not in cases.columns]

if missing:
    st.error(f"Missing columns in cases DataFrame: {missing}")
else:
    hearing_weight = st.slider("Days per hearing", 10, 50, 20)
    year_weight = st.slider("Year effect (days)", 5, 30, 10)
    baseline = st.slider("Baseline days", 50, 200, 100)

    # Rule-based prediction
    cases["predicted_disposal"] = (
        cases["total_hearings"] * hearing_weight +
        (cases["filing_year"] - cases["filing_year"].min()) * year_weight +
        baseline
    )

    st.subheader("Disposal Time Predictions (Rule-Based)")
    st.write(
        cases[["cnr_number", "total_hearings", "disposal_days", "predicted_disposal"]]
        .head(20)
    )

    # Line chart comparison
    st.line_chart(cases[["disposal_days", "predicted_disposal"]])

    from sklearn.metrics import mean_absolute_error
    mae = mean_absolute_error(cases["disposal_days"], cases["predicted_disposal"])
    st.success(f"Mean Absolute Error: {mae:.2f} days")
