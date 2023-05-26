import asyncio
import io
import os
import pickle
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from streamlit_chat import message

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')


async def main():
    async def store_doc_embeddings(file, filename):
        corpus = file.read().decode("utf-8")

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_text(corpus)

        embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        vectors = FAISS.from_texts(chunks, embeddings)

        with open(filename + ".pkl", "wb") as f:
            pickle.dump(vectors, f)

    async def get_doc_embeddings(file, filename):
        if not os.path.isfile(filename + ".pkl"):
            await store_doc_embeddings(file, filename)

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
    st.title("Document Chat")

    if 'ready' not in st.session_state:
        st.session_state['ready'] = False

    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])

    if uploaded_file is not None:
        with st.spinner("Processing..."):
            uploaded_file.seek(0)
            file = uploaded_file.read()

            if uploaded_file.type == "pdf":
                vectors = await get_doc_embeddings(io.BytesIO(file), uploaded_file.name)
                qa = ConversationalRetrievalChain.from_llm(
                    ChatOpenAI(model_name="gpt-3.5-turbo"),
                    retriever=vectors.as_retriever(),
                    return_source_documents=True
                )
            elif uploaded_file.type == "docx":
                vectors = await get_doc_embeddings(io.BytesIO(file), uploaded_file.name)
                qa = ConversationalRetrievalChain.from_llm(
                    ChatOpenAI(model_name="gpt-3.5-turbo"),
                    retriever=vectors.as_retriever(),
                    return_source_documents=True
                )
            elif uploaded_file.type == "txt":
                vectors = await get_doc_embeddings(io.BytesIO(file), uploaded_file.name)
                qa = ConversationalRetrievalChain.from_llm(
                    ChatOpenAI(model_name="gpt-                    3.5-turbo"),
                    retriever=vectors.as_retriever(),
                    return_source_documents=True
                )

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
        with st.form(key='my_form', clear_on_submit=True):
            user_input = st.text_input("Query:", placeholder="e.g: Summarize the document in a few sentences", key='input')
            submit_button = st.form_submit_button(label='Send')

            if submit_button and user_input:
                loop = asyncio.new_event_loop()
                output = await conversational_chat(user_input)
                loop.close()

                st.session_state['past'].append(user_input)
                st.session_state['generated'].append(output)

        if st.session_state['generated']:
            with response_container:
                for i in range(len(st.session_state['generated'])):
                    message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="thumbs")
                    message(st.session_state["generated"][i], key=str(i), avatar_style="fun-emoji")


if __name__ == "__main__":
    asyncio.run(main())

