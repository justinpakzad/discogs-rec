import streamlit as st
import re
import requests
from fast_api.utils import load_mappings

mappings = load_mappings()


def validate_url(url):
    pattern = r"https?://www\.discogs\.com/release/\d+(-[a-zA-Z0-9\-]+)?"
    if re.match(pattern, url):
        return True
    return False


def call_rec_api(discogs_url):
    url = "http://127.0.0.1:8000/recommend"
    payload = {"url": discogs_url, "n_recs": 7}
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        return f"Error: {e}"


st.title("Discogs Rec")
st.markdown(
    """
    <style>
        .custom-font {
            font-size:16px !important;
            font-weight:bold;
            color: white;
            text-shadow: 2px 2px 5px grey;
            margin-bottom: 20px;  /* Add bottom margin for spacing */
        }
    </style>
    <div class="custom-font">
        Discogs Rec uses the Approximate Nearest Neighbors algorithm to recommend records based on features extracted from the Discogs data dumps, as well as enriched features extracted via web scraping. The model is trained only on electronic music.
    </div>
    """,
    unsafe_allow_html=True,
)


url = st.text_input(
    "Enter a Discogs URL", placeholder="https://www.discogs.com/release/123456"
)
if url:
    if validate_url(url):
        recs = call_rec_api(url)
        if not isinstance(recs, str):
            for rec in recs:
                st.markdown(
                    f"<a href='{rec[2]}' class='custom-font'>{rec[0]} - {rec[1]}</a>",
                    unsafe_allow_html=True,
                )
        else:
            st.error("Sorry, the release is not in the scope of our model.")
    else:
        st.error(
            "Invalid URL, please make sure it takes the form https://www.discogs.com/release/<release_id>"
        )
