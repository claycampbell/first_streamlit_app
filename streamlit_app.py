import streamlit as st
import openai
import os
import PyPDF2

# Get the OpenAI API key from environment variables
api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = api_key

# Define the conversation with the model
def generate_responses(file_content, user_role, user_story):
    conversation = [
        {"role": "system", "content": "You are a technical business analyst."},
        {"role": "user", "content": "Here is a PDF document. Can you analyze it and provide information based on its content?"},
        {"role": "assistant", "content": file_content},
        {"role": "user", "content": user_role},
        {"role": "assistant", "content": user_story}
    ]

    # Call OpenAI Chat Completion API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
    )

    # Extract the response from the model's output
    user_story_response = response.choices[0].message.content
    return user_story_response


def main():
    st.title("PDF Assistant")

    st.write("Upload a PDF file to get information and facilitate discussions.")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        file_content = ""
        for page in pdf_reader.pages:
            file_content += page.extract_text()

        # Generate Ideas for User Stories
        if st.button("Generate Ideas for User Stories"):
            with st.spinner("Generating ideas..."):
                responses = generate_responses(file_content, "Generate ideas for user stories.", "")

            # Display Ideas
            for index, response in enumerate(responses, start=1):
                if response.startswith("Idea"):
                    st.write(f"{response}\n")
                else:
                    st.write(response)

                if response.startswith("Idea"):
                    user_story_button_id = f"user_story_button_{index}"
                    if st.button("Generate User Story", key=user_story_button_id):
                        user_story = response.split(": ")[1]
                        user_story_response = generate_responses(file_content, "Generate user story.", user_story)
                        st.write(f"User Story: {user_story_response}\n")

        # Explain Customer Benefits
        if st.button("Explain Customer Benefits"):
            with st.spinner("Explaining Benefits..."):
                responses = generate_responses(file_content, "What are the main benefits of this project for the customer?", "")
            st.success("Benefits Explained!")

            # Display Responses
            for index, response in enumerate(responses, start=1):
                st.write(f"Response {index}: {response}")

        # Estimate Effort and Identify Risks
        if st.button("Estimate Effort and Identify Risks"):
            with st.spinner("Estimating effort and identifying risks..."):
                responses = generate_responses(file_content, "What are the main tasks required to complete this project?", "")
            st.success("Effort Estimated and Risks Identified!")

            # Display Responses
            for index, response in enumerate(responses, start=1):
                st.write(f"Response {index}: {response}")


if __name__ == "__main__":
    main()
