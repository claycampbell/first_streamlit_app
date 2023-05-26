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
import openai

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

openai.api_key = api_key

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

    llm = ChatOpenAI(model_name="gpt-3.5-turbo")
    chain = load_qa_chain(llm, chain_type="stuff")

    if 'history' not in st.session_state:
        st.session_state['history'] = []

    # Creating the chatbot interface
    st.title("PDFChat :")

    if 'ready' not in st.session_state:
        st.session_state['ready'] = False

    uploaded_file = st.file_uploader("Choose a file", type="pdf")

    if uploaded_file is not None:
        with st.spinner("Processing..."):
            uploaded_file.seek(0)
            file = uploaded_file.read()
            vectors = await getDocEmbeds(io.BytesIO(file), uploaded_file.name)
            qa = ConversationalRetrievalChain.from_llm(ChatOpenAI(model_name="gpt-3.5-turbo"),
                                                      retriever=vectors.as_retriever(),
                                                      return_source_documents=True)

        st.session_state['ready'] = True

    st.divider()

    if st.session_state['ready']:
        if 'generated' not in st.session_state:
            st.session_state['generated'] = ["Welcome! You can now ask any questions regarding " + uploaded_file.name]

        if 'past' not in st.session_state:
            st.session_state['past'] = ["Hey!"]

        # Container for chat history
        response_container = st.container()

        # Container for text box
        container = st.container()

        with container:
            with st.form(key='my_form', clear_on_submit=True):
                user_input = st.text_input("Query:",
                                           placeholder="e.g: Summarize the paper in a few sentences",
                                           key='input')
                generate_button = st.form_submit_button("Generate User Stories")

            if generate_button:
                user_stories = await generate_user_stories()
                for story in user_stories:
                    st.session_state['generated'].append(story)

            if user_input and not generate_button:
                output = await conversational_chat(user_input)
                st.session_state['past'].append(user_input)
                st.session_state['generated'].append(output)

        if st.session_state['generated']:
            with response_container:
                for i in range(len(st.session_state['generated'])):
                    message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="thumbs")
                    message(st.session_state["generated"][i], key=str(i), avatar_style="fun-emoji")

async def generate_user_stories():
    user_stories = []

    prompt = "Generate user stories based on the provided document."

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100,
        n=5,  # Number of user stories to generate
        stop=None,  # Custom stop conditions if needed
        temperature=0.7,
    )

    for choice in response.choices:
        user_story = choice.text.strip()
        user_stories.append(user_story)

    return user_stories


if __name__ == "__main__":
    asyncio.run(main())
