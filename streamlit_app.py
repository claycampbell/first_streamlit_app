import streamlit as st
import openai
import os
import PyPDF2

# Get the OpenAI API key from environment variables
api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = api_key

# Define the conversation with the model
def generate_user_stories(file_content, user_role):
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Here is a PDF document. Can you analyze it and generate user stories based on its content?"},
        {"role": "assistant", "content": file_content},
        {"role": "user", "content": user_role}
    ]

    # Call OpenAI Chat Completion API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
    )

    # Extract the user stories from the model's response
    user_stories = []
    for choice in response.choices:
        output_text = choice.message.content
        user_stories.append(output_text)
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
                user_stories = generate_user_stories(file_content, "What are the acceptance criteria for these user stories?")

            st.success("User Stories Generated!")

            for index, story in enumerate(user_stories, start=1):
                st.write(f"User Story {index}: {story}")

        if st.button("Ask Another Question"):
            question = st.text_input("Enter your question:")
            if question:
                with st.spinner("Getting response..."):
                    user_stories = generate_user_stories(file_content, question)
                st.success("Response Generated!")

                for index, story in enumerate(user_stories, start=1):
                    st.write(f"Response {index}: {story}")


if __name__ == "__main__":
    main()
