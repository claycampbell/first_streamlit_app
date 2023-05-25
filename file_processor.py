import streamlit as st
import os
import openai

def process_file(file_contents):
    # Preprocess the file contents if necessary
    processed_text = preprocess_brd_text(file_contents)

    # Generate user stories using ChatGPT API
    user_stories = generate_user_stories(processed_text)

    return user_stories

def preprocess_brd_text(file_contents):
    # Implement your preprocessing logic here
    # This function should clean and format the text as needed
    # You can remove unnecessary sections, perform text cleaning, etc.
    processed_text = file_contents
    return processed_text

def generate_user_stories(processed_text):
    # Set up OpenAI API credentials
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    openai.api_key = openai_api_key

    # Generate user stories using OpenAI API
    response = openai.Completion.create(
        engine="text-davinci-0035-turbo",  # Use GPT-3.5 Turbo engine
        prompt=processed_text,
        max_tokens=1000,  # Adjust as needed
        temperature=0.7,  # Adjust as needed
        n=5,  # Number of user stories to generate
        stop=None,  # Stop condition to end the generated text, if necessary
        echo=True  # To include the prompt in the generated text
    )

    # Extract the generated user stories from the API response
    user_stories = response.choices[0].text.strip().split('\n')

    # Return the user stories
    return user_stories

# Main Streamlit app code
def main():
    # File upload and processing logic
    uploaded_file = st.file_uploader("Upload BRD file")
    if uploaded_file is not None:
        file_contents = uploaded_file.read().decode("utf-8")
        user_stories = process_file(file_contents)
        st.write("Generated User Stories:")
        for story in user_stories:
            st.write(story)

