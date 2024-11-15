import streamlit as st
from dotenv import load_dotenv
import os

# Title of the app
st.title("Cognitive Demo")

# Page selection
#page = st.sidebar.selectbox("Select a page:", ["Vision", "Speech", "Document"])
# Load variables from .env
load_dotenv('.env.local')

# Page selection
page = st.sidebar.selectbox("Select a page:", ["Vision", "Speech", "Document"])

# Display corresponding page
if page == "Vision":
    import pages.vision as vision
    vision.show_vision()
elif page == "Speech":
    import pages.speech as speech
    speech.show_speech()
elif page == "Document":
    import pages.document as document
    document.show_document()


