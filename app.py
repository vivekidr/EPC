import streamlit as st 
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe

# Set wide mode for more screen real estate
st.set_page_config(layout="wide")

# Google Sheets configuration
SPREADSHEET_ID = "1tf_zm894nO6We_WggGcoCeHf88chOlogH8mdHAU0fOs"
SHEET_NAME = "DhruvRathee"

# Hardcoded service account credentials
creds_info = {
    "type": "service_account",
    "project_id": "tweet-annotation-tool",
    "private_key_id": "e6f3a61a117638dceb9d11b7d698b4e2976aed73",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC0D9bWBikhhxCY\nHOy8x5j1ZJtpO0kk5cYv7lgmCI0Q6LeKkqGu4Xk8kDjOtjrg8aM8EJCrmVEy4PRb\nsQG/a/IvUG5DHGbkuLHKCf3bI6cMIBjvUghX4NPhUfAt7MO5BztAUpPx2LO/eHkD\nQkbQHuE+czC5tnJ1/aEEnYYAvILkAe+HDolCQdXKGMvOT2BWUXsgmos+aJ1LeJNb\n6R9eGOADZ1s/x4dJooMpxpE1qhN0P/KGEZYr/OPR/oJq2RM2IAivEj+9cfqVAmDf\nAu6iHPSxfdtNOzOJtimSuHanP8Mi1sMV218DcstDbcnddZEfdKi9kaJTFJUWJv2B\nRveCyVWrAgMBAAECggEABCv+60Y/1pIGsNQeKcWOr0RCL0FEiG8IucWSE9eDKcXY\nRRc6EA9ccryh1pljIUWqQPeVSV2r3vKfn+VfkSLS/PKBsBHM0jZhRwJf+A0carUT\nGkBkvfNaTD4Dnrg0ndb+6N+cWsKNlCsaQYZcA6hspQHpXvQofeTIVCF5oFgrf55J\nUMPCj1Wl+nRhaK0qAVsl1OnXl4CwqxTzOecQNO96bg2UHe+wLPDoL9xgqykLw0Mj\nGIksL/poXxdgFzwR3bqaakwX2PaIcEnwnl+YuFLsVX1xMiWuJp/kNBSdowGyTtBL\neL2qgSPvgoho5EJPBeTNKmnNQKMb6HzbvGCUpdzI8QKBgQDnF2seF6+F1qcJPToW\nwsCznNcivyHYyn4TDeS2SD9rjHPRRW5MGTIY8x/Vra4olA8JRpiEGSxG3CXUd4UK\nn+3EPg1CQNPTEQrVLnwh1lrheLak8r+VboXIekABJAdlXtKo9wzdYlpdNC8it8Gv\n5Ho4ULXzWb6thoeR+gLZlw3WcwKBgQDHeFgrnS5nJs4yh03qtszdLlD9xC81Kfmz\n3yEHeAZohnXuTTvmnep003I1yuRsZr8913PXts5Wnr/XWKCCu1pL5oqEcy8/SxxQ\npwZc3K2EFkD9ufoWC+l0Js67Lpn0PD5KpUxn3eiC7z/PR9h3MqyolFbKVTUOkxUJ\nreSwCtl96QKBgFmB0JOPSQTl5zzE4kL+m/T1wr5KmamGhN6MexG/WhEmDZX49oez\nGpxfTu1MoDBHaKuHFHvV5Dht/JkW0gkTeNyRzEDlKyaNa0y2/I1+oSTDxLqO63XN\noTPNZg0LD3JMD/wx9GGrPqTrGXaxBexC6rP1TwQ6togvm0MHOyNcRpfRAoGAOR0X\nOd22pKhyz/r372XKAOa7H/4lejZ7neocnfPa+eDOMZ6BsUW0FSFaCVb/0p4U0hM3\nwyM/r4Oi8Hka9HPKpgLr1ILam2fZQqqgYsR5FmH81+mBVwCwJqbZ+LSeNlVtjJgJ\n6Y+bfKoefi5XJ8Ilt9tJgoOlPngUxQG6gkGJBskCgYAlC7HGNImnP7hV9SspSVGr\nyKzTQpZbDmrcngbjP6n8Kr60YSIw0KRljQslB158RCpEal0yqEnz4naEYMFUEd1r\n4eRmDz4Cs8Ii0LfrQwG93XI1ALBbBJGDXM0X5FFVlDCMxthr7EwqHvMO+3EINF1q\n1+NM4jiTU7g9QEIPelBmXA==\n-----END PRIVATE KEY-----\n",
    "client_email": "sheets-access@tweet-annotation-tool.iam.gserviceaccount.com",
    "token_uri": "https://oauth2.googleapis.com/token"
}

def get_worksheet():
    """Authenticate and return the Google Sheets worksheet."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID)
    worksheet = sheet.worksheet(SHEET_NAME)
    return worksheet

def load_data():
    """Load tweet data from Google Sheets and ensure annotation columns exist."""
    worksheet = get_worksheet()
    df = get_as_dataframe(worksheet, evaluate_formulas=True)
    df = df.dropna(how="all")  # Remove completely empty rows if any
    for col in ['is_annotated', 'Economics', 'Political', 'Cultural', 'is_relevent']:
        if col not in df.columns:
            df[col] = False if col in ['is_annotated', 'is_relevent'] else None
    return df

def save_data(df):
    """Save the DataFrame back to Google Sheets."""
    worksheet = get_worksheet()
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
    st.experimental_rerun()

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
    .red-button button {
        background-color: red !important;
        color: white !important;
    }
    .green-button button {
        background-color: green !important;
        color: white !important;
    }
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
