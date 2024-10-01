from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import datetime
import os
import shutil  # For safe copying of files

load_dotenv()
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

# Base path for project
base_path = "D:\\TanDoori Data\\DataBase\\Projects\\AIDevelopment\\Project 015 - Story Generator"

# Creating Internet Search Tool
search_tool = SerperDevTool(site=["https://www.short-story.me/", "https://americanliterature.com/", "https://www.storynory.com/"])

# Defining LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    verbose=True,
    temperature=0.5,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Creating Agents
search_agent = Agent(
    role="Senior Researcher of Mysteries",
    goal=(
        "Uncover and analyze hidden secrets, narratives, and underlying themes behind the most mysterious stories "
        "on the topic of '{topic}'. Focus on finding connections, patterns, and obscure details that may not be immediately obvious."
    ),
    verbose=True,
    memory=True,
    backstory=(
        "As a seasoned researcher with a passion for uncovering hidden truths, you excel at dissecting complex narratives "
        "and piecing together unseen threads that connect them. You are driven by curiosity and the thrill of discovery."
    ),
    tools=[search_tool],
    llm=llm,
    allow_delegation=True,
    strategy=(
        "Begin by conducting a targeted web search for stories related to '{topic}' using the Web Search tool. "
        "Prioritize content from websites known for their obscure or mysterious stories. After identifying potential sources, "
        "use the Web Scraper tool to extract relevant content. Employ the LLM to analyze, summarize, and synthesize findings, "
        "focusing on hidden meanings, recurring themes, and unexpected patterns."
    ),
    decision_framework=(
        "1. Conduct an initial search to gather a wide range of story sources.\n"
        "2. Filter and prioritize stories based on relevance and potential for hidden details.\n"
        "3. Use memory to track findings and identify connections between different stories.\n"
        "4. Utilize LLM for deeper analysis, summarization, and hypothesis generation.\n"
        "5. Delegate specific tasks (e.g., detailed scraping, additional searches) to specialized tools when needed."
    ),
    personality=(
        "You are meticulous, analytical, and always searching for patterns others might miss. "
        "You balance a methodical approach with creative thinking, enabling you to uncover hidden layers "
        "within even the most enigmatic stories."
    ),
    feedback_loop_enabled=True,
    feedback_loop_details=(
        "1. Regularly evaluate the effectiveness of search strategies and refine them based on outcomes.\n"
        "2. Adjust the focus and parameters of subsequent searches based on findings and identified gaps.\n"
        "3. Collaborate with the writer agent to align future research with content creation needs."
    )
)

writer_agent = Agent(
    role="Creative Writer and Storyteller",
    goal=(
        "Transform research insights provided by the search agent into compelling and creative content. "
        "Your objective is to craft narratives, summaries, or articles that bring to life the hidden secrets, "
        "mysteries, and themes discovered in the stories. Ensure the content is engaging, coherent, and "
        "tailored to the intended audience."
    ),
    verbose=True,
    memory=True,
    backstory=(
        "As an accomplished writer with a passion for uncovering the hidden depths of stories, you have "
        "the unique ability to captivate readers through masterful storytelling. Your experience spans "
        "various genres, and you are particularly skilled at weaving together intricate plots, rich "
        "characters, and thought-provoking themes."
    ),
    llm=llm,
    allow_delegation=False,
    strategy=(
        "Utilize research outputs to identify key elements and themes of the stories. Develop narratives "
        "by expanding on these elements, incorporating vivid descriptions, emotional resonance, and creative "
        "storytelling techniques. Regularly reference the core findings from the search agent to maintain "
        "alignment with the original discoveries."
    ),
    content_guidelines=(
        "1. **Audience Focus**: Write for an audience interested in mystery and narrative analysis.\n"
        "2. **Narrative Flow**: Ensure a logical progression of ideas, from introduction to conclusion.\n"
        "3. **Engagement**: Use engaging hooks, cliffhangers, and questions to keep readers interested.\n"
        "4. **Clarity**: Maintain clarity and coherence, avoiding overly complex language or structures."
    ),
    creativity_mode=True,
    inspiration_sources=[
        "Contemporary fiction, classic mysteries, psychological thrillers, and narrative analysis."
    ],
    personality=(
        "You are imaginative, articulate, and love diving deep into complex narratives. Your writing is "
        "characterized by a unique blend of creativity and analytical depth, making each story both engaging "
        "and insightful."
    ),
    feedback_loop_enabled=True,
    feedback_loop_details=(
        "1. Regularly analyze reader engagement and feedback to refine future content.\n"
        "2. Adapt content styles and themes based on what resonates most with the audience.\n"
        "3. Collaborate with the search agent to align future content with new discoveries and story elements."
    )
)

# Validation Agent
validation_agent = Agent(
    role="Content Validator",
    goal=(
        "Review and validate the research and story outputs provided by the search and writer agents. "
        "Determine if the findings and the content are accurate, relevant, and coherent. "
        "If the results meet the criteria, write the story to a Markdown (.md) file."
    ),
    verbose=True,
    memory=True,
    backstory=(
        "You are a meticulous editor with a keen eye for detail, tasked with ensuring the quality of research "
        "and storytelling content. Your job is to verify the accuracy, consistency, and relevance of all outputs."
    ),
    llm=llm,
    allow_delegation=True,
    validation_strategy=(
        "1. Review the findings from the search agent to check for accuracy, completeness, and relevance to the topic.\n"
        "2. Examine the content generated by the writer agent for coherence, engagement, and adherence to the specified guidelines.\n"
        "3. If both outputs are validated, write the content to a Markdown (.md) file using `output_file`.\n"
        "4. If any output fails validation, provide feedback and re-run the appropriate agents."
    ),
    criteria=(
        "1. **Accuracy**: Are the research findings factually correct and relevant to the topic?\n"
        "2. **Completeness**: Has all necessary information been included in the research and story?\n"
        "3. **Coherence**: Does the story flow logically from beginning to end?\n"
        "4. **Engagement**: Is the content engaging and does it meet the audience's expectations?\n"
        "5. **Alignment**: Does the generated story align with the insights uncovered during research?"
    ),
    feedback_loop_enabled=True,
    feedback_loop_details=(
        "1. Provide feedback to the search and writer agents on areas needing improvement.\n"
        "2. Track any changes and enhancements made by the agents.\n"
        "3. Repeat the validation process until the outputs are acceptable."
    )
)

# Title Agent
title_agent = Agent(
    role="Title Generator",
    goal=(
        "Generate a compelling and descriptive title for the story based on its content. "
        "The title should capture the essence of the story, be intriguing, and attract the target audience."
    ),
    verbose=True,
    memory=False,
    backstory=(
        "You have an excellent sense for identifying the key themes and emotions in any story. "
        "Your goal is to create a title that draws readers in while accurately reflecting the story's core."
    ),
    llm=llm,
    allow_delegation=False,
    strategy=(
        "Analyze the main themes, emotions, and plot points of the story. Combine these insights to craft a title "
        "that is both intriguing and descriptive."
    ),
)

# Researching Task with search_tool
research_task = Task(
    description=(
        "Conduct an in-depth search to uncover compelling and unique stories related to the topic of '{topic}'. "
        "Your search should include:\n"
        "1. **Story Discovery**: Identify and retrieve stories that are relevant to the topic. Focus on finding narratives that are intriguing, unique, or have an element of mystery.\n"
        "2. **Story Analysis**: Analyze the identified stories to extract key elements such as plot, characters, themes, and narrative style. Highlight any distinctive features or trends present in these stories.\n"
        "3. **Summary and Insights**: Provide a summary of the most compelling stories found. Include insights into what makes these stories notable and how they fit into the broader context of the topic. Identify common themes or patterns that emerge from the stories.\n"
        "Ensure that your report is well-organized, with clear sections for story discovery, analysis, and summary. Use examples and quotes from the stories where applicable to support your findings."
    ),
    expected_output=(
        "A well-structured report consisting of three sections:\n"
        "1. **Story Discovery**: A detailed list of identified stories related to the topic, including their sources and a brief description.\n"
        "2. **Story Analysis**: An analysis of the stories, covering key narrative elements such as plot, characters, and themes.\n"
        "3. **Summary and Insights**: A summary of the most compelling stories with insights into their significance and common themes or patterns."
    ),
    tools=[search_tool],
    agent=search_agent,
)

# Writing Task with output_file
write_task = Task(
    description=(
        "Compose a validated story based on the findings from the search agent, on the topic of '{topic}'."
        "Search Agent Findings: <p>{findings}</p>"
        "Ensure the content is accurate, coherent, and engaging."
    ),
    expected_output="A Markdown file containing the final story.",
    agent=writer_agent,
    async_execution=False,
    tools=[search_tool],
    output_file='temp-story.md'
)

validation_task = Task(
    description=(
        "Review and validate the research and story outputs provided by the search and writer agents. "
        "Ensure that the findings are accurate and relevant, and the content is engaging, coherent, and adheres to guidelines. "
        "Return a binary value: '1' if validation is successful and the content is correct, or '0' if validation fails. "
        "If validation is successful, ensure that the output only contains the binary value. "
        "If the output contains additional Markdown content or other information, process it accordingly, extracting only the validation result. "
        "Topic of story: {topic}\n"
        "Findings of researcher agent: <p>{findings}</p>\n"
        "Content of writer agent: <p>{content}</p>"
    ),
    expected_output=(
        "Binary value (0 or 1) indicating validation success or failure. Ensure that only this binary value is returned. "
        "If additional content is present, it should be disregarded in terms of validation result extraction."
    ),
    agent=validation_agent,
    async_execution=False,
)

# Title Generation Task
title_task = Task(
    description=(
        "Based on the validated story written by write agent, generate the title of the story."
        "<story>{validated_story}</story>"
        "Generate accurate title, do not add any files extension."
    ),
    expected_output="Just story title, with extraneous characters removed. Only alphanumeric characters.",
    agent=title_agent,
    async_execution=False,
    tools=[search_tool],
)

def generate_index():
    """Generate a unique index for log files."""
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def main(topic, retry_limit=3):
    """Main execution flow for story generation."""
    attempt = 0
    while attempt < retry_limit:
        try:
            # Researching
            research = Crew(
                tasks=[research_task],
                agents=[search_agent],
                tools=[search_tool],
            )
            story_details = research.kickoff(inputs={'topic': topic})  # Searching on internet

            # Writing
            write = Crew(
                tasks=[write_task],
                agents=[writer_agent],
            )
            story_content = write.kickoff(inputs={'topic': topic, 'findings': story_details})  # Writing Story

            # Validation
            validation = Crew(
                tasks=[validation_task],
                agents=[validation_agent],
                tools=[search_tool],
            )
            validation_result = validation.kickoff(inputs={'topic': topic, 'findings': story_details, 'content': story_content})
            print(f"\n\n\n\n\n\n\n\n\n\n\nValidation result: {validation_result}, Type: {type(validation_result)}\n\n\n\n\n\n\n\n\n\n\n")

            # Title Generation
            title_generation = Crew(
                tasks=[title_task],
                agents=[title_agent],
            )

            if int(validation_result) == 1:
                title = title_generation.kickoff(inputs={'validated_story': story_content})

                # Moving file to output path
                output_path = os.path.join(base_path, "data")
                os.rename("temp-story.md", f"{title}.md")
                shutil.move(os.path.join(base_path, f"{title}.md"), os.path.join(output_path, f"{title}.md"))
                print(f"Story has been successfully saved as '{output_path}\\{title}.md'")
                break  # Exit loop if successful
            else:
                # Validation failed, log the issue
                logs_path = os.path.join(base_path, "logs")
                index = generate_index()
                shutil.move("temp-story.md", os.path.join(logs_path, f"{index}.md"))
                print(f"Logs saved at {logs_path} with file name {index}.md")
                print("Validation failed, re-running agents...")
                attempt += 1
        except Exception as e:
            print(f"An error occurred: {e}")
            attempt += 1
            if attempt >= retry_limit:
                print("Max retries reached. Process terminated.")

if __name__ == "__main__":
    # Getting story topic as input from user
    topic = input("Enter a story topic: ")
    main(topic)