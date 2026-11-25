import streamlit as st

def add_scroll_sky():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(
                180deg,
                #72c8ff 0%,
                #b9e5ff 25%,
                #ffb56b 50%,
                #493c85 75%,
                #050817 100%
            ) !important;
            background-attachment: fixed !important;
        }

        [data-testid="stAppViewContainer"] {
            background: transparent !important;
        }

        [data-testid="stHeader"] {
            background: transparent !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )