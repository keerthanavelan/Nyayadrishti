import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from helpers.sidebar import render_sidebar

st.set_page_config(
    page_title="Anomaly Detection",
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

# LOAD DATA
def load_data(
    cases_path = Path(__file__).parent.parent / "data/ISDMHack_Cases_students.csv",
    hearings_path = Path(__file__).parent.parent / "data/ISDMHack_Hear_students.csv"
    ):
    """Load cases and hearings CSV files."""
    cases = pd.read_csv(cases_path)
    hearings = pd.read_csv(hearings_path).copy()

    # Normalize CNR number safely
    if "cnr_number" in hearings.columns:
        hearings.loc[:, "cnr_number"] = hearings["cnr_number"].astype(str)

    return cases, hearings

# ------------------------------------------------------
# CLEAN CASES
# ------------------------------------------------------
def clean_cases(cases: pd.DataFrame) -> pd.DataFrame:
    """Clean cases dataset: normalize dates, compute durations, fill missing values."""
    possible_date_filed = ["Date_filed", "Filing_Date", "Filed_Date", "date_filed"]
    possible_decision_date = ["Decision_date", "Disposed_Date", "DecisionDate", "decision_date"]

    date_filed_col = next((c for c in possible_date_filed if c in cases.columns), None)
    decision_date_col = next((c for c in possible_decision_date if c in cases.columns), None)

    if date_filed_col:
        cases.loc[:, date_filed_col] = pd.to_datetime(cases[date_filed_col], errors="coerce")
    if decision_date_col:
        cases.loc[:, decision_date_col] = pd.to_datetime(cases[decision_date_col], errors="coerce")

    if date_filed_col and decision_date_col:
        cases.loc[:, "Case_Duration"] = (cases[decision_date_col] - cases[date_filed_col]).dt.days
    else:
        cases.loc[:, "Case_Duration"] = np.nan

    if cases["Case_Duration"].dropna().empty:
        cases.loc[:, "Case_Duration"] = cases["Case_Duration"].fillna(0)
    else:
        cases.loc[:, "Case_Duration"] = cases["Case_Duration"].fillna(cases["Case_Duration"].median())

    numeric_cols = cases.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        median_val = cases[col].median()
        if np.isnan(median_val):
            cases.loc[:, col] = cases[col].fillna(0)
        else:
            cases.loc[:, col] = cases[col].fillna(median_val)

    return cases

# ------------------------------------------------------
# ISOLATION FOREST ANOMALY DETECTION
# ------------------------------------------------------
def detect_anomalies(cases: pd.DataFrame, contamination=0.05) -> pd.DataFrame:
    """Run Isolation Forest anomaly detection on numeric columns."""
    numeric_cols = cases.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        st.error("No numeric columns available for anomaly detection!")
        return cases

    iso = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=42
    )
    iso.fit(cases[numeric_cols])

    cases.loc[:, "Anomaly"] = iso.predict(cases[numeric_cols])
    cases.loc[:, "Anomaly_Flag"] = (cases["Anomaly"] == -1)
    cases.loc[:, "Anomaly_Score"] = iso.decision_function(cases[numeric_cols])

    return cases

# ------------------------------------------------------
# STREAMLIT DASHBOARD
# ------------------------------------------------------
def run_dashboard():
    st.title("Anomaly Detection Dashboard")

    # Sidebar controls
    contamination = st.sidebar.slider("Contamination Rate (fraction anomalies)", 0.01, 0.20, 0.05, 0.01)

    #st.write("Loading data...")
    cases, hearings = load_data()

    #st.write("Cleaning dataset...")
    cases = clean_cases(cases)

    #st.write("Detecting anomalies...")
    cases = detect_anomalies(cases, contamination=contamination)

    st.success("Here are the first few anomalies:")
    st.dataframe(cases[cases["Anomaly_Flag"]].head())

    # Histogram of anomaly scores
    st.subheader("Distribution of Anomaly Scores")
    fig, ax = plt.subplots(figsize=(5,3))
    sns.histplot(cases["Anomaly_Score"], bins=30, kde=True, color="blue", ax=ax)
    ax.set_xlabel("Anomaly Score")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)

    # Scatter plot: Case Duration vs Disposal Days
    if "Case_Duration" in cases.columns and "disposal_days" in cases.columns:
        st.subheader("Case Duration vs Disposal Days")
        fig, ax = plt.subplots(figsize=(5,3))
        sns.scatterplot(
            data=cases,
            x="Case_Duration", y="disposal_days",
            hue="Anomaly_Flag", palette={True:"red", False:"green"}, alpha=0.6, ax=ax
        )
        st.pyplot(fig)

    # Box plot of Case Duration
    st.subheader("Box Plot of Case Duration")
    fig, ax = plt.subplots(figsize=(6,5))
    sns.boxplot(x=cases["Case_Duration"], ax=ax)
    st.pyplot(fig)

    # Full anomalies table
    st.subheader("All Detected Anomalies")
    st.dataframe(cases[cases["Anomaly_Flag"]])

# ------------------------------------------------------
# MAIN ENTRY
# ------------------------------------------------------
if __name__ == "__main__":
    run_dashboard()