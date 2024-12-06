import streamlit as st
import re
import requests


def validate_url(url):
    pattern = r"https?://www\.discogs\.com/release/\d+(-[a-zA-Z0-9\-]+)?"
    if re.match(pattern, url):
        return True
    return False


def call_rec_api(
    discogs_url,
    endpoint_url="http://discogs_rec_app:8000/recommend",
):
    payload = {"url": discogs_url, "n_recs": 7}
    try:
        response = requests.post(endpoint_url, json=payload)
        return response.json()
    except Exception as e:
        return f"Error: {e}"


def fetch_recommendations(url):
    response = call_rec_api(url)
    if isinstance(response, str):
        return None, "Sorry, the release is not in the scope of our model."
    return response, None


def display_recommendations(recs):
    for rec in recs:
        st.markdown(
            f"<a href='{rec[2]}' class='custom-font'>{rec[0]} - {rec[1]}</a>",
            unsafe_allow_html=True,
        )


def main():
    st.title("Discogs Rec")
    url = st.text_input(
        "Enter a Discogs URL", placeholder="https://www.discogs.com/release/123456"
    )
    if url:
        if validate_url(url):
            recs, error_message = fetch_recommendations(url)
            if error_message:
                st.write(error_message)
            else:
                display_recommendations(recs)
        else:
            st.error(
                "Invalid URL, please make sure it takes the form https://www.discogs.com/release/<release_id>"
            )


if __name__ == "__main__":
    main()
