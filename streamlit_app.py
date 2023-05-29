import openai
from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
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
    response = await openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a business analyst assistant."},
            {"role": "user", "content": query},
        ]
    )
    result = response.choices[0].message.content
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

# Load the OpenAI API key
openai.api_key = api_key

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

# ...

llm = openai

# ...

# Replace the usage of ChatOpenAI with OpenAI API
chat_model = openai

# ...

# Run the Streamlit app
if __name__ == "__main__":
    main()
