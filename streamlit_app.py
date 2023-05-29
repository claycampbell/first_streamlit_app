import streamlit as st
import openai
import os
import PyPDF2

# Get the OpenAI API key from environment variables
api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = api_key

# Define the conversation with the model
def generate_user_stories(file_content):
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Here is a PDF document. Can you analyze it and generate user stories based on its content?"},
        {"role": "assistant", "content": file_content}
    ]

    # Call OpenAI Chat Completion API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
    )

    # Extract the user stories from the model's response
    user_stories = []
    for message in response['choices'][0]['message']['content']:
        if message['role'] == 'assistant' and message['content']:
            user_stories.append(message['content']['text'])
    return user_stories


def main():
    st.title("PDF User Stories Generator")

    st.write("Upload a PDF file to generate user stories.")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        file_content = ""
        for page in pdf_reader.pages:
            file_content += page.extract_text()

        if st.button("Generate User Stories"):
            with st.spinner("Generating user stories..."):
                user_stories = generate_user_stories(file_content)

            st.success("User Stories Generated!")

            for index, story in enumerate(user_stories, start=1):
                st.write(f"User Story {index}: {story}")


if __name__ == "__main__":
    main()
