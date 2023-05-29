from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from pathlib import Path
from dotenv import load_dotenv
import os
import streamlit as st
from streamlit_chat import message
import io
import asyncio
import pickle

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
    result = await chat_model.generate(query)
    st.session_state['history'].append((query, result))
    return result

def display_output(output):
    st.session_state['generated'].append(output)
    with response_container:
        message(output, key=str(len(st.session_state['generated']) - 1), avatar_style="fun-emoji")

async def generate_user_stories():
    prompt = "Take this document and turn it into user stories that I can give my engineering team to begin development."
    result = await conversational_chat(prompt)
    display_output(result)

def summarize_document():
    # Implementation of the "Summarize Document" functionality
    pass

def extract_key_topics():
    # Implementation of the "Extract Key Topics" functionality
    pass

def identify_stakeholders():
    # Implementation of the "Identify Stakeholders" functionality
    pass

def create_feature_list():
    # Implementation of the "Create Feature List" functionality
    pass

def generate_use_cases():
    # Implementation of the "Generate Use Cases" functionality
    pass

# Load the OpenAI chat model
chat_model = ChatOpenAI(model_name="gpt-3.5-turbo")

# Create the Streamlit app
st.title("Business Analyst AI Agent")

# Define the response container
response_container = st.empty()

# Initialize session state if not exists
if 'history' not in st.session_state:
    st.session_state['history'] = []

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

# Add the buttons
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

if st.button("Generate User Stories"):
    asyncio.run(generate_user_stories())

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
        qa = chat_model
