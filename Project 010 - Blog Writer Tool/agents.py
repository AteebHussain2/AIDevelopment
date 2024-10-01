#conda activate "D:\Multiagent project\agent21"

import os
from crewai import Agent
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from tools import tool

load_dotenv()

# call gemini model

llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    verbose=True,
    temperature=0.5,
    google_api_key=os.getenv("GOOGLE_API_KEY")
    )

# create a senior resecher with memory and verbose mode

news_researcher = Agent(
    role = "Senior Researcher",
    goal = "Uncover ground breaking technologies in {topic}",
    verbose = True,
    memory = True,
    backstory = ("Driven by curiosity, yu are at the forefront of innovation, eager to explore and share knowladge that could chnage the world."),
    tools = [tool],
    llm = llm,
    allow_delegation = True
)

# Creating a writer agent

news_writer = Agent(
    role = "Writer",
    goal = "Write interesting tech stories about {topic}",
    verbose = True,
    memory = True,
    backstory = ("With a flair of simplyfying complex topics, you craft angaging narrative that captivate and educate and bringing new discoveries to light in an accesable manner."),
    tools = [tool],
    llm = llm,
    allow_delegation = False
)