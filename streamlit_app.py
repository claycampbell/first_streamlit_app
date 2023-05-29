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

        option = st.selectbox("Select an option:", ("Generate Ideas for User Stories", "Facilitate Team Discussions", "Estimate Effort and Identify Risks"))

        if option == "Generate Ideas for User Stories":
            user_role = st.text_input("Enter your role:", "Generate ideas for user stories.", key="user_role_text")
        elif option == "Facilitate Team Discussions":
            user_role = st.selectbox("Select a question:", ("What are the main benefits of this feature for the customer?", "What are the key requirements for this feature to be successful?", "What are some potential challenges or limitations of this feature?"), key="user_role_dropdown")
        elif option == "Estimate Effort and Identify Risks":
            user_role = st.selectbox("Select a question:", ("What tasks are dependent on the completion of task X?", "Which tasks will be impacted if task Y is delayed?"), key="user_role_dropdown")
        else:
            user_role = ""

        if st.button("Submit", key="submit_button") and user_role:
            with st.spinner("Processing..."):
                responses = generate_responses(file_content, user_role)
                st.success("Task Completed!")

                for index, response in enumerate(responses, start=1):
                    st.write(f"Response {index}: {response}")
        elif st.button("Submit", key="submit_button"):
            st.warning("Please select a question.")

if __name__ == "__main__":
    main()
