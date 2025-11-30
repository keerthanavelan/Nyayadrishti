import pandas as pd
import streamlit as st
import warnings
import logging
import os

os.environ['PYTHONWARNINGS'] = 'ignore::DeprecationWarning'
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".st.cache.")
warnings.simplefilter("ignore", category=DeprecationWarning)

# Suppress Streamlit's internal logger
logging.getLogger("streamlit").setLevel(logging.ERROR)
logging.getLogger("streamlit.delta_generator").setLevel(logging.ERROR)

# Suppress via Streamlit's internal warning system
try:
    import streamlit.logger as st_logger
    st_logger.get_logger("streamlit").setLevel(logging.ERROR)
except:
    pass

# -------------------------------
# Step 1: Load Data
# -------------------------------
@st.cache_data(ttl=3600)   # caches for 1 hour
def load_data():
    from pathlib import Path

    base_dir = Path(__file__).parent

    cases_path = base_dir / "data" / "ISDMHack_Cases_students.csv"
    hearings_path = base_dir / "data" / "ISDMHack_Hear_students.csv"



    cases = pd.read_csv(cases_path)
    hearings = pd.read_csv(hearings_path)

    return cases, hearings

# -------------------------------
# Step 2: Normalize column names
# -------------------------------   
def normalize_columns(df):
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
    return df

# -------------------------------
# Step 3: Clean Cases Data
# -------------------------------
def clean_cases(cases):
    cases = normalize_columns(cases)

    col_map = {
        'cnr_number': 'cnr_number',
        'date_filed': 'date_filed',
        'decision_date': 'decision_date',
        'registration_date': 'registration_date'
    }
    cases.rename(columns=col_map, inplace=True)

    # Convert dates safely
    for col in ['date_filed', 'decision_date', 'registration_date']:
        if col in cases.columns:
            cases[col] = pd.to_datetime(cases[col], errors='coerce')

    # Calculate disposal_days if possible
    if 'date_filed' in cases.columns and 'decision_date' in cases.columns:
        cases['disposal_days'] = (cases['decision_date'] - cases['date_filed']).dt.days + 1

    # Filing year
    if 'date_filed' in cases.columns:
        cases['filing_year'] = cases['date_filed'].dt.year

    # Ensure total_hearings column exists
    if 'total_hearings' not in cases.columns:
        cases['total_hearings'] = 0

    # Drop duplicate CNRs
    if 'cnr_number' in cases.columns:
        cases = cases.drop_duplicates(subset='cnr_number')
        cases['cnr_number'] = cases['cnr_number'].astype(str)

    return cases

# -------------------------------
# Step 4: Clean Hearings Data
# -------------------------------
def clean_hearings(hearings):
    hearings = normalize_columns(hearings).copy()

    # Convert dates
    if 'businessondate' in hearings.columns:
        hearings['business_on_date'] = pd.to_datetime(hearings['businessondate'], errors='coerce')

    # Drop duplicate CNRs
    if 'cnr_number' in hearings.columns:
        hearings = hearings.drop_duplicates(subset='cnr_number')
        hearings.loc[:, 'cnr_number'] = hearings['cnr_number'].astype(str)

    return hearings

# -------------------------------
# Step 5: Memory-safe merge
# -------------------------------
def merge_data(cases, hearings, chunk_size=100000):
    merged_chunks = []
    for start in range(0, len(hearings), chunk_size):
        chunk = hearings.iloc[start:start+chunk_size]
        merged_chunk = chunk.merge(cases, on='cnr_number', how='left')
        merged_chunks.append(merged_chunk)
    merged_data = pd.concat(merged_chunks, ignore_index=True)
    return merged_data

# -------------------------------
# Example usage
# -------------------------------
if __name__ == "__main__":
    cases, hearings = load_data()
    cases = clean_cases(cases)
    hearings = clean_hearings(hearings)
    merged_data = merge_data(cases, hearings)

    print(merged_data.head())
    print(f"Total rows after merge: {len(merged_data)}")
