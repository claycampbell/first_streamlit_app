import streamlit as st
import os
from file_processor import process_file

# Set page title and icon
st.set_page_config(page_title="User Story Generation", page_icon=":memo:")

# File upload
st.title("User Story Generation")
uploaded_file = st.file_uploader("Upload your Business Requirements Document (BRD)", type="txt")

# Process file and generate user stories
if uploaded_file is not None:
    file_contents = uploaded_file.read().decode("utf-8")
    user_stories = process_file(file_contents)

    # Display user stories
    st.header("Generated User Stories")
    for i, story in enumerate(user_stories, start=1):
        st.write(f"User Story {i}: {story}")
