import os
import logging
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI  # Import Google's LLM
from crewai import Agent, Task, Process, Crew
from crewai_tools import SerperDevTool  # Import SerperDevTool for internet search
from langchain_community.agent_toolkits.load_tools import load_tools
from dotenv import load_dotenv
import datetime
import shutil

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
base_path = os.path.dirname(os.path.abspath(__file__))

# To load Human in the loop
search_tool = SerperDevTool(config={"api_key": os.getenv("SERPER_API_KEY")})

# Defining LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    verbose=True,
    temperature=0.5,
    google_api_key=os.getenv("GOOGLE_API_KEY")  # Use Google's API key
)

reporter = Agent(
    role="News Reporter",
    goal="Find and report the latest news on the topic defined by {user_prompt}",
    backstory="""You are an Expert News Reporter who knows how to find the latest and most relevant news on any given topic. 
    You excel at searching the internet for the most recent news articles, summarizing them, and presenting them in a clear and engaging manner.
    """,
    verbose=True,
    allow_delegation=False,
    tools=[search_tool],
    llm=llm,
)

critic = Agent(
    role="Expert Writing Critic",
    goal="Provide feedback and criticize news article drafts. Make sure that the tone and writing style is compelling, simple, and concise",
    backstory="""You are an Expert at providing feedback to the news writers. You can tell when a news article isn't concise,
    simple, or engaging enough. You know how to provide helpful feedback that can improve any text. You know how to make sure that text 
    stays informative and insightful by using layman terms.
    """,
    verbose=True,
    allow_delegation=True,
    llm=llm,
)

task_news_report = Task(
    description="""Use and summarize scraped data from the internet to make a detailed news report on the latest news on the topic defined by {user_prompt}. Use ONLY 
    data from the internet to generate the report. Your final answer MUST be a full news report, text only, ignore any code or anything that 
    isn't text. The report has to have bullet points and with 5-10 latest news articles. Write names of every news source and article. 
    Each bullet point MUST contain 3 sentences that refer to one specific news article or source you found on the internet.  
    """,
    expected_output="A detailed news report on the topic: {user_prompt}.",
    agent=reporter,
)

task_news_article = Task(
    description="""Write a news article with text only and with a short but impactful headline and at least 10 paragraphs. The article should summarize 
    the news report on topic {user_prompt}. Style and tone should be compelling and concise, fun, and engaging for the general public. Name specific news sources and articles in the world. Don't 
    write "**Paragraph [number of the paragraph]:**", instead start the new paragraph in a new line. Write names of news sources and articles in BOLD.
    ALWAYS include links to news sources/articles. ONLY include information from the internet.
    """,
    expected_output='A well-written news article summarizing the latest news from the internet.',
    agent=reporter,
    output_file="data/temp-news-report.md"
)

task_critique = Task(
    description="""The Output MUST have the markdown format.
    Make sure that it does and if it doesn't, rewrite it accordingly.
    Make sure that the article is pretty and nice to read.
    """,
    expected_output="A critique of the news article ensuring it meets the required format and style.",
    agent=critic,
)

title_agent = Agent(
    role="Title Generator",
    goal="Generate a compelling and descriptive title for the news report based on its content. The title should capture the essence of the report, be intriguing, and attract the target audience.",
    verbose=True,
    memory=False,
    backstory="""You have an excellent sense for identifying the key themes and emotions in any report. Your goal is to create a title that draws readers in while accurately reflecting the report's core.""",
    llm=llm,
    allow_delegation=False,
    strategy="""Analyze the main themes, emotions, and plot points of the report. Combine these insights to craft a title that is both intriguing and descriptive.""",
)

title_task = Task(
    description="""Based on the validated report content, generate the title of the report.
    <report>{validated_report}</report>
    Generate accurate title, do not add any files extension.""",
    expected_output="Just report title, with extraneous characters removed. Only alphanumeric characters.",
    agent=title_agent,
    async_execution=False,
    tools=[search_tool],
)

def generate_index():
    """Generate a unique index for log files."""
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def NewsLetter(user_prompt, retry_limit=3):
    attempt = 0
    while attempt < retry_limit:
        try:
            # instantiate crew of agents
            crew = Crew(
                agents=[reporter, critic],
                tasks=[task_news_report, task_news_article, task_critique],
                verbose=2,
                process=Process.sequential,  # Sequential process will have tasks executed one after the other and the outcome of the previous one is passed as extra content into this next.
            )
            
            # Get your crew to work!
            result = crew.kickoff(inputs={'user_prompt': user_prompt})
            logging.info("Newsletter generation completed successfully")
            
            # Title Generation
            title_generation = Crew(
                tasks=[title_task],
                agents=[title_agent],
            )
            title = title_generation.kickoff(inputs={'validated_report': result})
            logging.info("Title Generation Completed Successfully")
            
            # Moving file to output path
            timestamp = generate_index()
            output_path = os.path.join(base_path, "data")
            temp_report_path = os.path.join(output_path, "temp-news-report.md")
            final_report_path = os.path.join(output_path, f"{title}_{timestamp}.md")

            if os.path.exists(temp_report_path):
                os.rename(temp_report_path, final_report_path)
                logging.info(f"Report has been successfully saved as '{final_report_path}'")
            else:
                logging.error(f"Error: The file '{temp_report_path}' does not exist.")

            return {
                "title": title,
                "content": result,
            }

        except Exception as e:
            logging.error(f"An error occurred on attempt {attempt + 1}: {e}")
            attempt += 1
            if attempt >= retry_limit:
                logging.error("Max retries reached. Process terminated.")
                return None