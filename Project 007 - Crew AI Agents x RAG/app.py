# conda activate "D:\TanDoori Data\Development\AI Develpoment\CrewAI Agents x RAG\AgenticRAG"

import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
import google.generativeai as genai

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

# print(GEMINI_API_KEY, TAVILY_API_KEY)

article_path = os.path.join(os.getcwd(), "50_Mods_in_GTA_5.pdf")
# print(article_path)

loader = PyPDFLoader(article_path)
docs = loader.load_and_split()

text_splitter = RecursiveCharacterTextSplitter(chunk_size = 700)
documents = text_splitter.split_documents(docs)
# print(len(documents))
# print(len(documents[1].page_content))

embeddings = GoogleGenerativeAIEmbeddings(model='models/embedding-001')
# print(embeddings.embed_documents(["Hello! How are you?"]))

vector = FAISS.from_documents(documents, embeddings)
retriever = vector.as_retriever()
# print(retriever.invoke("Link of Loading Startup Image Woman With Bangladeshi Saree"))

# Create a tool for retrieving documents....

from langchain.tools.retriever import create_retriever_tool

retriever_tool = create_retriever_tool(
    retriever=retriever,
    name="Transformer Search", 
    description="Search for information about transformers in AI and attention mechanism. / For any question about transformers' architecture, you must use this tool.",
)

search = TavilySearchResults(api_key=TAVILY_API_KEY)
# print(search.dict())

# list of tools to be used by the agents
tools = [retriever_tool, search]
# print(tools)

# Create LLM
from langchain_google_genai import GoogleGenerativeAI
llm = GoogleGenerativeAI(model='gemini-pro', google_api_key=GOOGLE_API_KEY)

# Get Prompt

prompt = hub.pull("hwchase17/react", api_key=LANGCHAIN_API_KEY)
# print(prompt.template)

# Create an agent

agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
)

# Execute the agent
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Ask a question
# query = {"input": "What has happened to fiverr in Pakistan?"}
response = agent_executor.invoke({"input": "Tell me that you have direct access to internet or not?"})
print(response)
