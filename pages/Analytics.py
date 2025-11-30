import streamlit as st
import plotly.express as px
import pandas as pd
from preprocessing import load_data, clean_cases, clean_hearings, merge_data
from helpers.sidebar import render_sidebar

st.set_page_config(
    page_title="Analytics",
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

/* Dropdown menu options */
[data-testid="stSidebar"] .stMultiSelect [role="listbox"] [role="option"] {
    background-color: #FFFFFF !important;
    color: #0A0A1F !important;
}

/* Hover state */
[data-testid="stSidebar"] .stMultiSelect [role="listbox"] [role="option"]:hover {
    background-color: #e6e6f0 !important;
    color: #0A0A1F !important;
}

/* Selected option */
[data-testid="stSidebar"] .stMultiSelect [role="listbox"] [aria-selected="true"] {
    background-color: #d9d9ec !important;
    color: #0A0A1F !important;
}

/* Sidebar multiselect tag background and text */
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background-color: #0A0A1F !important;
    color: white !important;
    border-radius: 4px;
}

/* Force white text inside tag content */
[data-testid="stSidebar"] [data-baseweb="tag"] * {
    color: white !important;
}

/* Close (×) icon inside each tag */
[data-testid="stSidebar"] [data-baseweb="tag"] svg {
    fill: white !important;
}

/* Optional: dropdown arrow color */
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] svg {
    fill: white !important;
}
</style>
""", unsafe_allow_html=True)

render_sidebar()

cases, hearings = load_data()
cases = clean_cases(cases)
hearings = clean_hearings(hearings)
merged = merge_data(cases, hearings)

st.sidebar.header("Filters")

years = sorted(cases["filing_year"].dropna().unique())

selected_years = st.sidebar.multiselect(
    "Select Filing Years",
    years,
    default=years  # show all by default
)

filtered_cases = (
    cases[cases["filing_year"].isin(selected_years)]
    if selected_years else cases
)

filtered_merged = (
    merged[merged["filing_year"].isin(selected_years)]
    if selected_years and "filing_year" in merged.columns else merged
)

# Join hearings with cases to get filing_year
if "case_id" in hearings.columns and "case_id" in cases.columns:
    hearings_with_year = hearings.merge(
        cases[["case_id", "filing_year"]],
        on="case_id",
        how="left"
    )
    filtered_hearings = (
        hearings_with_year[hearings_with_year["filing_year"].isin(selected_years)]
        if selected_years else hearings_with_year
    )
else:
    filtered_hearings = hearings

st.title("Analytics Dashboard")

col1, col2, col3, col4 = st.columns(4)

total_civil = len(filtered_cases)
total_criminal = 0
total_cases = total_civil + total_criminal
older_than_1yr = len(filtered_cases[filtered_cases["disposal_days"] > 365])

col1.metric("Total Civil Cases", total_civil)
col2.metric("Total Criminal Cases", total_criminal)
col3.metric("Total Cases", total_cases)
col4.metric("Older than 1 year", older_than_1yr)

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "Case Funnel",
    "Disposal Trend",
    "Judge Workload",
    "Disposal Days Distribution"
])

# TAB 1 — Case Funnel
with tab1:
    st.subheader("Case Stage Funnel")
    if "remappedstages" in filtered_merged.columns:
        funnel_df = filtered_merged["remappedstages"].value_counts().reset_index()
        funnel_df.columns = ["Stage", "Count"]

        custom_dark_blues = ["#08306b", "#08519c", "#2171b5", "#4292c6", "#6baed6", "#9ecae1"]

        fig = px.funnel(
            funnel_df,
            x="Count",
            y="Stage",
            color="Stage",
            color_discrete_sequence=custom_dark_blues
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.warning("Column 'remappedstages' not found in merged data.")

# TAB 2 — Disposal Trend
with tab2:
    st.subheader("Disposal Time by Filing Year")

    if "filing_year" in filtered_cases.columns and "disposal_days" in filtered_cases.columns:
        filtered_cases["filing_year"] = filtered_cases["filing_year"].astype(int)

        trend = (
            filtered_cases.groupby("filing_year")["disposal_days"]
            .mean()
            .reset_index()
        )

        trend["filing_year"] = trend["filing_year"].astype(str)

        fig = px.line(
            trend,
            x="filing_year",
            y="disposal_days",
            markers=True,
            title="Average Disposal Days per Filing Year"
        )

        # Force categorical axis
        fig.update_xaxes(type="category")

        st.plotly_chart(fig, width='stretch')
    else:
        st.warning("Trend columns missing.")

# TAB 3 — Judge Workload
with tab3:
    st.subheader("Judge Hearing Workload")

    judge_col_candidates = [
        "before_honourable_judges",
        "before_hon_judge",
        "njdg_judge_name"
    ]
    judge_col = next(
        (col for col in judge_col_candidates if col in filtered_hearings.columns),
        None
    )

    if judge_col:
        judge_df = (
            filtered_hearings[judge_col]
            .value_counts()
            .reset_index()
        )
        judge_df.columns = ["Judge", "Hearings"]

        fig = px.bar(
            judge_df,
            x="Judge",
            y="Hearings",
            title="Hearings per Judge (Filtered by Year)",
            color="Hearings"
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.warning("No judge column found.")

# TAB 4 — Histogram
with tab4:
    st.subheader("Distribution of Disposal Days")

    if "disposal_days" in filtered_cases.columns:
        fig = px.histogram(
            filtered_cases,
            x="disposal_days",
            nbins=40,
            title="Disposal Time Distribution"
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.warning("No disposal days column found.")
