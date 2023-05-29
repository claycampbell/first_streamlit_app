import openai
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
import streamlit.components.v1 as components

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

# ...

async def main():
    # ...

    # Creating the chatbot interface
    st.title("PDFChat:")

    if 'ready' not in st.session_state:
        st.session_state['ready'] = False

    uploaded_file = st.file_uploader("Choose a file", type="pdf")

    if uploaded_file is not None:

        with st.spinner("Processing..."):
            # Add your code here that needs to be executed
            uploaded_file.seek(0)
            file = uploaded_file.read()
            vectors = await getDocEmbeds(io.BytesIO(file), uploaded_file.name)
            qa = ConversationalRetrievalChain.from_llm(ChatOpenAI(model_name="gpt-3.5-turbo"), retriever=vectors.as_retriever(), return_source_documents=True)

        st.session_state['ready'] = True

    st.divider()

    if st.session_state['ready']:
        # ...

        if submit_button and user_input:
            output = await conversational_chat(user_input)
            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)
        # ...

        if quick_message_1:
            output = await conversational_chat("What is the main topic of the paper?")
            st.session_state['past'].append("What is the main topic of the paper?")
            st.session_state['generated'].append(output)
        if quick_message_2:
            output = await conversational_chat("What are the main findings of the paper?")
            st.session_state['past'].append("What are the main findings of the paper?")
            st.session_state['generated'].append(output)
        if quick_message_3:
            output = await conversational_chat("What are the implications of the paper?")
            st.session_state['past'].append("What are the implications of the paper?")
            st.session_state['generated'].append(output)

        if st.session_state['generated']:
            with response_container:
                for i in range(len(st.session_state['generated'])):
                    message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="thumbs")
                    message(st.session_state["generated"][i], key=str(i), avatar_style="fun-emoji")

    # ...

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(st.asyncio.run(main()))
