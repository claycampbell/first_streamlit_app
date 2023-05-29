import streamlit as st
import openai
import os
import PyPDF2

# Get the OpenAI API key from environment variables
api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = api_key

# Define the conversation with the model
def generate_responses(file_content, user_role):
    conversation = [
        {"role": "system", "content": "You are a technical business analyst."},
        {"role": "user", "content": "Here is a PDF document. Can you analyze it and provide information based on its content?"},
        {"role": "assistant", "content": file_content},
        {"role": "user", "content": user_role}
    ]

    # Call OpenAI Chat Completion API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
    )

    # Extract the responses from the model's output
    responses = []
    for choice in response.choices:
        response_text = choice.message.content
        responses.append(response_text)
    return responses


def main():
    st.title("PDF Assistant")

    st.write("Upload a PDF file to get information and facilitate discussions.")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        file_content = ""
        for page in pdf_reader.pages:
            file_content += page.extract_text()

        selected_option = st.selectbox("Select an option:", ("Generate Ideas for User Stories", "Facilitate Team Discussions", "Estimate Effort and Identify Risks"))

        if st.button("Submit"):
            with st.spinner("Processing..."):
                if selected_option == "Generate Ideas for User Stories":
                    user_role = "Generate ideas for user stories."
                elif selected_option == "Facilitate Team Discussions":
                    user_role = "What are the main benefits of this feature for the customer?"
                elif selected_option == "Estimate Effort and Identify Risks":
                    user_role = "What tasks are dependent on the completion of task X?"
                else:
                    user_role = ""

                if user_role:
                    responses = generate_responses(file_content, user_role)
                    st.success("Task Completed!")

                    for index, response in enumerate(responses, start=1):
                        st.write(f"Response {index}: {response}")
                else:
                    st.warning("Please select an option.")

if __name__ == "__main__":
    main()
