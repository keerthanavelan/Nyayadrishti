import streamlit as st
import pandas as pd
from preprocessing import load_data, clean_cases

st.title("ML Predictions")

# Load and clean data
cases, hearings = load_data()
cases = clean_cases(cases)

# Show available columns for debugging
# st.write("Available columns in cases:", cases.columns.tolist())

# Defensive checks for required columns
required_cols = ["cnr_number", "disposal_days", "total_hearings", "filing_year"]
missing = [col for col in required_cols if col not in cases.columns]

if missing:
    st.error(f"Missing columns in cases DataFrame: {missing}")
else:
    # Interactive sliders for rule parameters
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

    # Add simple evaluation metric
    from sklearn.metrics import mean_absolute_error
    mae = mean_absolute_error(cases["disposal_days"], cases["predicted_disposal"])
    st.success(f"Mean Absolute Error: {mae:.2f} days")