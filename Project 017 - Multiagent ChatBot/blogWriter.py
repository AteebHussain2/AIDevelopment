import os
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
import datetime
import shutil

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
base_path = os.path.dirname(os.path.abspath(__file__))

# Define the language model (LLM)
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    verbose=True,
    temperature=0.5,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Create an agent to handle blog writing
writer = Agent(
    role="Senior Technical Writer",
    goal="Write an engaging and interesting blog post on any topic using simple, accessible language.",
    backstory="""You are an experienced writer skilled in creating compelling, engaging, and informative blog posts on a variety of topics.
    You explain complex ideas in an easy-to-understand way, making content enjoyable for a broad audience.""",
    verbose=True,
    allow_delegation=True,
    llm=llm,
)

# Define the task to create a blog on any user-specified topic
task_blog = Task(
    description="""Write a comprehensive and engaging blog article on the topic specified by the user. 
    The blog should have:
    - A catchy and descriptive title.
    - An introduction that outlines the main points or purpose of the blog.
    - At least 5 to 10 paragraphs, each with its own subheading, explaining different aspects or key points of the topic.
    - Each section should contain specific facts, examples, or actionable tips that are relevant to the topic.
    - A conclusion that summarizes the key points and encourages the reader to take action or reflect on the topic.
    <user_prompt>{user_prompt}</user_prompt>
    """,
    expected_output='A well-structured and engaging blog post on the given topic.',
    agent=writer,
    output_file="data/temp-report.md"
)

# Create an agent to generate the title
title_agent = Agent(
    role="Title Generator",
    goal="Generate a compelling and descriptive title for the blog based on its content. The title should capture the essence of the blog, be intriguing, and attract the target audience.",
    verbose=True,
    memory=False,
    backstory="""You have an excellent sense for identifying the key themes and emotions in any blog. Your goal is to create a title that draws readers in while accurately reflecting the blog's core.""",
    llm=llm,
    allow_delegation=False,
    strategy="""Analyze the main themes, emotions, and plot points of the blog. Combine these insights to craft a title that is both intriguing and descriptive.""",
)

# Define the task to generate the title
title_task = Task(
    description="""Based on the validated blog content, generate the title of the blog.
    <blog>{validated_blog}</blog>
    Generate an accurate title, do not add any file extensions.""",
    expected_output="Just the blog title, with extraneous characters removed. Only alphanumeric characters. Don't use special characters.",
    agent=title_agent,
    async_execution=False,
)

def generate_index():
    """Generate a unique index for log files."""
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def BlogWriter(user_prompt, retry_limit=3):
    attempt = 0
    try:
        # Instantiate crew of agents
        crew = Crew(
            agents=[writer],
            tasks=[task_blog],
            verbose=2,
            process=Process.sequential,
        )
        
        # Get your crew to work!
        result = crew.kickoff(inputs={'user_prompt': user_prompt})
        logging.info("Blog generation completed successfully.")
        
        # Title Generation
        title_generation = Crew(
            tasks=[title_task],
            agents=[title_agent],
        )
        title = title_generation.kickoff(inputs={'validated_blog': result})
        logging.info("Title Generation Completed Successfully")
        
        # Save the generated blog
        timestamp = generate_index()
        output_path = os.path.join(base_path, "data")
        temp_report_path = os.path.join(output_path, "temp-report.md")
        final_report_path = os.path.join(output_path, f"{title}_{timestamp}.md")
        
        if os.path.exists(temp_report_path):
            os.rename(temp_report_path, final_report_path)
            logging.info(f"Blog has been successfully saved as '{final_report_path}'")
            
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