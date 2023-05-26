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

def store_doc_embeddings(file, filename):
    reader = PdfReader(file)
    corpus = ''.join([p.extract_text() for p in reader.pages if p.extract_text()])
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(corpus)
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    vectors = FAISS.from_texts(chunks, embeddings)
    with open(filename + ".pkl", "wb") as f:
        pickle.dump(vectors, f)

def get_doc_embeddings(file, filename):
    if not os.path.isfile(filename + ".pkl"):
        store_doc_embeddings(file, filename)
    with open(filename + ".pkl", "rb") as f:
        vectors = pickle.load(f)
    return vectors

async def conversational_chat(query):
    result = await qa({"question": query, "chat_history": st.session_state['history']})
    st.session_state['history'].append((query, result["answer"]))
    return result["answer"]

def display_output(output):
    st.session_state['generated'].append(output)
    with response_container:
        message(output, key=str(len(st.session_state['generated']) - 1), avatar_style="fun-emoji")

def generate_user_stories():
    prompt = {"question": "Take this document and turn it into user stories that I can give my engineering team to begin development.", "chat_history": st.session_state['history']}
    result = await qa(prompt)
    display_output(result["answer"])

if st.button("Generate User Stories"):
    await generate_user_stories()


def summarize_document():
    prompt = "Please provide a summary of the document."
    output = conversational_chat(prompt)
    st.session_state['history'].append(("Summarize Document", output))
    return output

def extract_key_topics():
    prompt = "What are the key topics covered in this document?"
    output = conversational_chat(prompt)
    st.session_state['history'].append(("Extract Key Topics", output))
    return output

def identify_stakeholders():
    prompt = "Who are the stakeholders mentioned in the document?"
    output = conversational_chat(prompt)
    st.session_state['history'].append(("Identify Stakeholders", output))
    return output

def create_feature_list():
    prompt = "Based on the document, what are the features that should be included?"
    output = conversational_chat(prompt)
    st.session_state['history'].append(("Create Feature List", output))
    return output

def generate_use_cases():
    prompt = "Generate use cases based on the document."
    output = conversational_chat(prompt)
    st.session_state['history'].append(("Generate Use Cases", output))
    return output

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
        vectors = get_doc_embeddings(io.BytesIO(file), uploaded_file.name)
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
            output = conversational_chat(user_input)
            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)

    if st.session_state['generated']:
        with response_container:
            for i in range(len(st.session_state['generated'])):
                message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="thumbs")
                message(st.session_state["generated"][i], key=str(i), avatar_style="fun-emoji")

    if st.button("Generate User Stories"):
        generate_user_stories()

    if st.button("Summarize Document"):
        summarize_document()

    if st.button("Extract Key Topics"):
        extract_key_topics()

    if st.button("Identify Stakeholders"):
        identify_stakeholders()

    if st.button("Create Feature List"):
        create_feature_list()

    if st.button("Generate Use Cases"):
        generate_use_cases()
