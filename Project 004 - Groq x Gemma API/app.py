import streamlit as st
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from langchain_groq import ChatGroq
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

groq_api_key = os.getenv("Groq_API_Key")
os.environ["google_api_key"] = os.getenv("Google_API_Key")

st.title("Gemma Rag Model With Groq")

llm = ChatGroq(groq_api_key = groq_api_key,
                model_name = "Llama3-8b-8192")

prompt = ChatPromptTemplate.from_template(
    """
    Answer the questions based on the provided context only.
    Please provide the most accurate response based on the question]
    <context>
    {context}
    </context>
    Questions: {input}
    """
)

def vector_embedding():
    if "vectors" not in st.session_state:
        st.session_state.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        st.session_state.loader = PyPDFDirectoryLoader("data/")
        st.session_state.docs = st.session_state.loader.load()
        st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size = 10000, chunk_overlap = 1000)
        st.session_state.final_documents = st.session_state.text_splitter.split_documents(st.session_state.docs[::])
        st.session_state.vectors = FAISS.from_documents(st.session_state.final_documents, st.session_state.embeddings)

prompt1 = st.text_input("Enter your questions from directory....")

if st.button("Document Embeddings"):
    vector_embedding()
    st.write("Vector Store DB is ready to use....")

import time

if prompt1:
    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = st.session_state.vectors.as_retriever()
    retriever_chain = create_retrieval_chain(retriever, document_chain)
    start = time.process_time()
    response = retriever_chain.invoke({'input': prompt1})
    print("Response time: ", time.process_time()-start)
    st.write(response['answer'])

    with st.expander("Document Search References"):
        for i, doc in enumerate(response['context']):
            st.write(doc.page_content)
            st.write("------------")