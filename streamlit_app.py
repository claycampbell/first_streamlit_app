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

        # Create columns for buttons and responses
        col1, col2 = st.beta_columns(2)

        # Generate Ideas for User Stories
        if col1.button("Generate Ideas for User Stories"):
            with st.spinner("Generating ideas..."):
                responses = generate_responses(file_content, "Generate ideas for user stories.")
            st.success("Ideas Generated!")

            # Display Responses
            with col2:
                for index, response in enumerate(responses, start=1):
                    st.write(f"Idea {index}: {response}")

        # Explain Customer Benefits
        if col1.button("Explain Customer Benefits"):
            with st.spinner("Explaining Benefits..."):
                responses = generate_responses(file_content, "What are the main benefits of this project for the customer?")
            st.success("Benefits Explained!")

            # Display Responses
            with col2:
                for index, response in enumerate(responses, start=1):
                    st.write(f"Response {index}: {response}")

        # Estimate Effort and Identify Risks
        if col1.button("Estimate Effort and Identify Risks"):
            with st.spinner("Estimating effort and identifying risks..."):
                responses = generate_responses(file_content, "What are the main tasks required to complete this project?")
            st.success("Effort Estimated and Risks Identified!")

            # Display Responses
            with col2:
                for index, response in enumerate(responses, start=1):
                    st.write(f"Response {index}: {response}")


if __name__ == "__main__":
    main()
