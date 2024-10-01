from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

# Base path for project
base_path = os.path.dirname(os.path.abspath(__file__))

# Creating Internet Search Tool
search_tool = SerperDevTool(
    site=[
        "https://www.wikipedia.org/",
        "https://www.britannica.com/",
        "https://www.nytimes.com/",
    ]
)

# Defining LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    verbose=True,
    temperature=0.5,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

# Creating Agents
search_agent = Agent(
    role="Internet Researcher",
    goal=(
        "Conduct a comprehensive search on the internet to gather information on the topic of '{query}'. "
        "Focus on finding accurate, relevant, and up-to-date information from reliable sources."
    ),
    verbose=True,
    memory=True,
    backstory=(
        "As an experienced internet researcher, you excel at finding accurate and relevant information from a variety of sources. "
        "You are driven by a passion for knowledge and a commitment to uncovering the truth."
    ),
    tools=[search_tool],
    llm=llm,
    allow_delegation=True,
    strategy=(
        "Begin by conducting a targeted web search for information related to '{query}' using the Web Search tool. "
        "Prioritize content from reliable and authoritative sources. After identifying potential sources, "
        "use the Web Scraper tool to extract relevant content. Employ the LLM to analyze, summarize, and synthesize findings, "
        "focusing on accuracy, relevance, and comprehensiveness."
    ),
    decision_framework=(
        "1. Conduct an initial search to gather a wide range of sources.\n"
        "2. Filter and prioritize sources based on reliability and relevance.\n"
        "3. Use memory to track findings and identify connections between different sources.\n"
        "4. Utilize LLM for deeper analysis, summarization, and synthesis.\n"
        "5. Delegate specific tasks (e.g., detailed scraping, additional searches) to specialized tools when needed."
    ),
    personality=(
        "You are meticulous, analytical, and always searching for the most accurate and relevant information. "
        "You balance a methodical approach with a passion for uncovering the truth."
    ),
    feedback_loop_enabled=True,
    feedback_loop_details=(
        "1. Regularly evaluate the effectiveness of search strategies and refine them based on outcomes.\n"
        "2. Adjust the focus and parameters of subsequent searches based on findings and identified gaps.\n"
        "3. Collaborate with other agents to align future research with content creation needs."
    ),
)

writer_agent = Agent(
    role="Creative Writer",
    goal=(
        "Transform research insights provided by the search agent into a coherent and informative response. "
        "Your objective is to craft a response that accurately reflects the findings and provides clear, concise, and engaging information to the user."
    ),
    verbose=True,
    memory=True,
    backstory=(
        "As a skilled writer with a knack for turning complex information into clear and engaging content, "
        "you excel at synthesizing research findings into informative responses. Your goal is to provide users with accurate and helpful information."
    ),
    llm=llm,
    allow_delegation=False,
    strategy=(
        "Utilize research outputs to identify key elements and themes. Develop a response by expanding on these elements, "
        "incorporating clear explanations, relevant details, and engaging language. Regularly reference the core findings from the search agent to maintain alignment with the original discoveries."
    ),
    content_guidelines=(
        "1. **Clarity**: Ensure the response is clear and easy to understand.\n"
        "2. **Accuracy**: Provide accurate information based on the research findings.\n"
        "3. **Engagement**: Use engaging language to keep the user interested.\n"
        "4. **Relevance**: Ensure the response is relevant to the user's query."
    ),
    creativity_mode=True,
    inspiration_sources=[
        "Reliable sources, authoritative websites, and well-researched articles."
    ],
    personality=(
        "You are articulate, insightful, and dedicated to providing accurate and engaging information. "
        "Your writing is characterized by clarity, precision, and a deep understanding of the subject matter."
    ),
    feedback_loop_enabled=True,
    feedback_loop_details=(
        "1. Regularly analyze user feedback to refine future responses.\n"
        "2. Adapt content styles and themes based on what resonates most with users.\n"
        "3. Collaborate with the search agent to align future responses with new findings and insights."
    ),
)

# Researching Task with search_tool
research_task = Task(
    description=(
        "Conduct an in-depth search to gather accurate and relevant information on the topic of '{query}'. "
        "Your search should include:\n"
        "1. **Source Discovery**: Identify and retrieve information from reliable and authoritative sources.\n"
        "2. **Source Analysis**: Analyze the identified sources to extract key information and insights. Highlight any distinctive features or trends present in the information.\n"
        "3. **Summary and Insights**: Provide a summary of the most relevant information found. Include insights into what makes this information notable and how it fits into the broader context of the topic. Identify common themes or patterns that emerge from the sources.\n"
        "Ensure that your report is well-organized, with clear sections for source discovery, analysis, and summary. Use examples and quotes from the sources where applicable to support your findings."
    ),
    expected_output=(
        "A well-structured report consisting of three sections:\n"
        "1. **Source Discovery**: A detailed list of identified sources related to the topic, including their URLs and a brief description.\n"
        "2. **Source Analysis**: An analysis of the sources, covering key information and insights.\n"
        "3. **Summary and Insights**: A summary of the most relevant information with insights into its significance and common themes or patterns."
    ),
    tools=[search_tool],
    agent=search_agent,
)

# Writing Task
write_task = Task(
    description=(
        "Compose a response based on the findings from the search agent, on the topic of '{query}'."
        "Ensure the response is accurate, coherent, and engaging."
    ),
    expected_output="A well-written response based on the research findings.",
    agent=writer_agent,
    async_execution=False,
    tools=[search_tool],
)


def WebSearcher(query):
    """Main execution flow for web search and response generation."""
    try:
        # Researching
        research = Crew(
            tasks=[research_task, write_task],
            agents=[search_agent, writer_agent],
            tools=[search_tool],
        )
        response = research.kickoff(inputs={"query": query})  # Generating Response
        print("\n\nResponse Generation Completed Successfully...\n\n")

        return response

    except Exception as e:
        print(f"An error occurred: {e}")
        return None