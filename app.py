import streamlit as st 
import pandas as pd
import os
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe

# Set wide mode for more screen real estate
st.set_page_config(layout="wide")

# Google Sheets configuration
SPREADSHEET_ID = "1tf_zm894nO6We_WggGcoCeHf88chOlogH8mdHAU0fOs"
SHEET_NAME = "DhruvRathee"
CREDS_FILE = "creds.json"

def get_worksheet():
    """Authenticate and return the Google Sheets worksheet."""
    credentials = st.secrets["gcp_service_account"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    
    creds = Credentials.from_service_account_info(credentials, scopes=scopes)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(SPREADSHEET_ID)  # Ensure SPREADSHEET_ID is correct
    return sheet.worksheet(SHEET_NAME)  # Ensure SHEET_NAME exists

def load_data():
    """Load tweet data from Google Sheets and ensure annotation columns exist."""
    worksheet = get_worksheet()
    df = get_as_dataframe(worksheet, evaluate_formulas=True)
    # Remove completely empty rows if any
    df = df.dropna(how="all")
    # Ensure annotation columns exist
    for col in ['is_annotated', 'Economics', 'Political', 'Cultural', 'is_relevent']:
        if col not in df.columns:
            df[col] = False if col in ['is_annotated', 'is_relevent'] else None
    return df

def save_data(df):
    """Save the DataFrame back to Google Sheets."""
    worksheet = get_worksheet()
    # Write the DataFrame to the sheet, resizing if necessary
    set_with_dataframe(worksheet, df, include_index=False, resize=True)

def annotate_tweet(df, tweet_index, ratings, is_relevent):
    """Annotate the tweet with the ratings and save progress."""
    for topic in ['Economics', 'Political', 'Cultural']:
        value = ", ".join(ratings[topic]) if ratings[topic] else "N/A"
        df.loc[tweet_index, topic] = value
    df.loc[tweet_index, "is_relevent"] = is_relevent
    df.loc[tweet_index, "is_annotated"] = True
    save_data(df)
    st.success("Annotation saved!")
    st.rerun()

# Custom CSS for grid alignment, centered checkboxes, and colored buttons
st.markdown(
    """
    <style>
    .grid-cell {
        border: 1px solid #ccc;
        padding: 10px;
        min-width: 50px;
        min-height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .grid-header {
        font-weight: bold;
        background-color: #f0f0f0;
    }
    /* Colored button wrappers */
    .red-button button {
        background-color: red !important;
        color: white !important;
    }
    .green-button button {
        background-color: green !important;
        color: white !important;
    }
    /* Center the checkbox element */
    .stCheckbox > label {
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True
)

# Load tweet data from Google Sheets
df = load_data()
unannotated = df[df["is_annotated"] != True]
if unannotated.empty:
    st.write("All tweets have been annotated!")
    st.stop()

# Get the first unannotated tweet
tweet_index = unannotated.index[0]
tweet = unannotated.loc[tweet_index]

# Two-column layout: left for tweet details, right for annotation form
left_col, right_col = st.columns([1, 3])

with right_col:
    with st.form(key="annotation_form"):
        st.markdown(f"by <b>{tweet['Handle']}</b>", unsafe_allow_html=True)
        st.markdown(f"<b>{tweet['Content']}</b>", unsafe_allow_html=True)
        
        st.markdown("#### Select Ratings")
        # Build header row for the grid (Topic + ratings 1-7)
        header_cols = st.columns(8)
        with header_cols[0]:
            st.markdown('<div class="grid-cell grid-header">Topic</div>', unsafe_allow_html=True)
        for i in range(1, 8):
            with header_cols[i]:
                st.markdown(f'<div class="grid-cell grid-header">{i}</div>', unsafe_allow_html=True)
        
        # Build a row per topic with centered checkboxes.
        topics = ["Economics", "Political", "Cultural"]
        ratings = {}
        for topic in topics:
            ratings[topic] = []
            row = st.columns(8)
            with row[0]:
                st.markdown(f'<div class="grid-cell grid-header">{topic}</div>', unsafe_allow_html=True)
            for i in range(1, 8):
                with row[i]:
                    if st.checkbox("", key=f"{tweet_index}_{topic}_{i}", label_visibility="collapsed"):
                        ratings[topic].append(str(i))
                        
        button_cols = st.columns(2)
        with button_cols[0]:
            st.markdown('<div class="red-button">', unsafe_allow_html=True)
            submit_irrel = st.form_submit_button("X (Irrelevant)")
            st.markdown("</div>", unsafe_allow_html=True)
        with button_cols[1]:
            st.markdown('<div class="green-button">', unsafe_allow_html=True)
            submit_rel = st.form_submit_button("✔ (Submit)")
            st.markdown("</div>", unsafe_allow_html=True)
        
        if submit_irrel:
            annotate_tweet(df, tweet_index, ratings, is_relevent=False)
        if submit_rel:
            annotate_tweet(df, tweet_index, ratings, is_relevent=True)
