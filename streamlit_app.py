import streamlit as st
import os
import openai

# Set page title and icon
st.set_page_config(page_title="User Story Generation", page_icon=":memo:")

# Set up OpenAI API credentials
os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']


# Preprocess function (if needed)
def preprocess_brd_text(file_contents):
    # Implement your preprocessing logic here
    # This function should clean and format the text as needed
    # You can remove unnecessary sections, perform text cleaning, etc.
    processed_text = file_contents
    return processed_text

# User story generation function
def generate_user_stories(processed_text):
    # Generate user stories using OpenAI API
   response = openai.Completion.create(
    engine="gpt-3.5-turbo",
    prompt=processed_text,
    max_tokens=1000,
    temperature=0.7,
    n=5,
    stop=None,
    echo=True
)


    # Extract the generated user stories from the API response
    user_stories = response.choices[0].text.strip().split('\n')

    # Return the user stories
    return user_stories

# File upload and user story generation
st.title("User Story Generation")
uploaded_file = st.file_uploader("Upload your Business Requirements Document (BRD)", type="txt")

if uploaded_file is not None:
    file_contents = uploaded_file.read().decode("utf-8")
    processed_text = preprocess_brd_text(file_contents)
    user_stories = generate_user_stories(processed_text)

    # Display user stories
    st.header("Generated User Stories")
    for i, story in enumerate(user_stories, start=1):
        st.write(f"User Story {i}: {story}")
