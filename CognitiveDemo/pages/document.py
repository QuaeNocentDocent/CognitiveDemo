import streamlit as st

def show_document():
    # Combo box for selection
    model_type = st.selectbox("Select Model Type:", ["Standard", "Fine Tuned"])

    st.header("Document Page")
    st.write(f"You selected: {model_type}")
    # Add more functionality for the Document page here
