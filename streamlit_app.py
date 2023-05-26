from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
import pickle
from pathlib import Path
from dotenv import load_dotenv
import os
import streamlit as st
from streamlit_chat import message
import io
import asyncio

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

async def main():

    async def storeDocEmbeds(file, filename):
        reader = PdfReader(file)
        corpus = ''.join([p.extract_text() for p in reader.pages if p.extract_text()])
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_text(corpus)
        embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        vectors = FAISS.from_texts(chunks, embeddings)
        with open(filename + ".pkl", "wb") as f:
            pickle.dump(vectors, f)

    async def getDocEmbeds(file, filename):
        if not os.path.isfile(filename + ".pkl"):
            await storeDocEmbeds(file, filename)
        with open(filename + ".pkl", "rb") as f:
            vectors = pickle.load(f)
        return vectors

    async def conversational_chat(query):
        result = qa({"question": query, "chat_history": st.session_state['history']})
        st.session_state['history'].append((query, result["answer"]))
        return result["answer"]

    def generate_user_stories():
        prompt = {"question": "Take this document and turn it into user stories that I can give my engineering team to begin development.", "chat_history": st.session_state['history']}
        _ = qa(prompt)
        return

    def generate_use_cases():
        prompt = {"question": "Generate use cases based on the document.", "chat_history": st.session_state['history']}
        _ = qa(prompt)
        return

    def create_ui_mockups():
        prompt = {"question": "Create user interface mockups based on the document.", "chat_history": st.session_state['history']}
        _ = qa(prompt)
        return

    def generate_test_cases():
        prompt = {"question": "Generate test cases based on the document.", "chat_history": st.session_state['history']}
        _ = qa(prompt)
        return

    def collaborate_and_comment():
        prompt = {"question": "Enable collaboration and commenting for the document.", "chat_history": st.session_state['history']}
        _ = qa(prompt)
        return

    def generate_system_diagrams():
        prompt = {"question": "Generate system diagrams based on the document.", "chat_history": st.session_state['history']}
        _ = qa(prompt)
        return

    llm = ChatOpenAI(model_name="gpt-3.5-turbo")

    if 'history' not in st.session_state:
        st.session_state['history'] = []

    st.title("PDFChat:")

    if 'ready' not in st.session_state:
        st.session_state['ready'] = False

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        with st.spinner("Processing..."):
            uploaded_file.seek(0)
            file = uploaded_file.read()
            vectors = await getDocEmbeds(io.BytesIO(file), uploaded_file.name)
            qa = ConversationalRetrievalChain.from_llm(llm, retriever=vectors.as_retriever(), return_source_documents=True)
        st.session_state['ready'] = True

    st.divider()

    if st.session_state['ready']:
        if 'generated' not in st.session_state:
            st.session_state['generated'] = ["Welcome! You can now ask any questions regarding " + uploaded_file.name]
        if 'past' not in st.session_state:
            st.session_state['past'] = ["Hey!"]

        response_container = st.container()
        container = st.container()

        with container:
            with st.form(key='my_form', clear_on_submit=True):
                user_input = st.text_input("Query:", placeholder="e.g: Summarize the paper in a few sentences", key='input')
                submit_button = st.form_submit_button(label='Send')

            if submit_button and user_input:
                output = await conversational_chat(user_input)
                st.session_state['past'].append(user_input)
                st.session_state['generated'].append(output)

        if st.session_state['generated']:
            with response_container:
                for i in range(len(st.session_state['generated'])):
                    message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="thumbs")
                    message(st.session_state["generated"][i], key=str(i), avatar_style="fun-emoji")

        st.subheader("Actions:")

        # Button for generating user stories
        if st.button("Generate User Stories"):
            st.button("Generate User Stories")
            generate_user_stories()
            await asyncio.sleep(1)  # Add a delay between API calls

        # Button for generating use cases
        if st.button("Generate Use Cases"):
            st.button("Generate Use Cases")
            generate_use_cases()
            await asyncio.sleep(1)  # Add a delay between API calls

        # Button for creating user interface mockups
        if st.button("Create User Interface Mockups"):
            st.button("Create User Interface Mockups")
            create_ui_mockups()
            await asyncio.sleep(1)  # Add a delay between API calls

        # Button for generating test cases
        if st.button("Generate Test Cases"):
            st.button("Generate Test Cases")
            generate_test_cases()
            await asyncio.sleep(1)  # Add a delay between API calls

        # Button for collaboration and commenting
        if st.button("Collaborate and Comment"):
            st.button("Collaborate and Comment")
            collaborate_and_comment()
            await asyncio.sleep(1)  # Add a delay between API calls

        # Button for generating system diagrams
        if st.button("Generate System Diagrams"):
            st.button("Generate System Diagrams")
            generate_system_diagrams()
            await asyncio.sleep(1)  # Add a delay between API calls

if __name__ == "__main__":
    asyncio.run(main())
