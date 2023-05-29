import streamlit as st
import openai
import os
import PyPDF2
import pandas as pd

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
            ideas = []
            for response in responses:
                if response.startswith("Idea"):
                    ideas.append(response)
            df_ideas = pd.DataFrame({"Ideas": ideas})
            st.table(df_ideas)

        # Explain Customer Benefits
        if st.button("Explain Customer Benefits"):
            with st.spinner("Explaining Benefits..."):
                responses = generate_responses(file_content, "What are the main benefits of this project for the customer?", "")
            st.success("Benefits Explained!")

            # Display Responses
            df_benefits = pd.DataFrame({"Responses": responses})
            st.table(df_benefits)

        # Estimate Effort and Identify Risks
        if st.button("Estimate Effort and Identify Risks"):
            with st.spinner("Estimating effort and identifying risks..."):
                responses = generate_responses(file_content, "What are the main tasks required to complete this project?", "")
            st.success("Effort Estimated and Risks Identified!")

            # Display Responses
            df_tasks = pd.DataFrame({"Responses": responses})
            st.table(df_tasks)

        # Generate User Story
        if st.button("Generate User Story"):
            user_story_input = st.text_input("Enter the idea number to generate a user story:", value="")
            if user_story_input:
                user_story_index = int(user_story_input) - 1
                if 0 <= user_story_index < len(responses):
                    idea = responses[user_story_index]
                    if idea.startswith("Idea"):
                        user_story = idea.split(": ")[1]
                        user_story_response = generate_responses(file_content, "Generate user story.", user_story)
                        st.write("Generated User Story:")
                        st.write(user_story_response)


if __name__ == "__main__":
    main()
