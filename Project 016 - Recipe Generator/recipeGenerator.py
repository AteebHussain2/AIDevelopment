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

# Creating Internet Search Tool for Recipe Sites
search_tool = SerperDevTool(site=["https://www.allrecipes.com/", "https://www.foodnetwork.com/", "https://www.seriouseats.com/"])

# Defining LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    verbose=True,
    temperature=0.5,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Creating Agents
search_agent = Agent(
    role="Recipe Researcher",
    goal=(
        "Discover and analyze popular, unique, and interesting recipes on the topic of '{topic}'. "
        "Focus on finding variations, ingredients, cooking methods, and cultural significance."
    ),
    verbose=True,
    memory=True,
    backstory=(
        "As a seasoned culinary researcher with a passion for discovering new and exciting recipes, "
        "you excel at finding unique dishes from various cuisines. You are driven by a love for food and creativity in cooking."
    ),
    tools=[search_tool],
    llm=llm,
    allow_delegation=True,
    strategy=(
        "Begin by conducting a targeted web search for recipes related to '{topic}' using the Web Search tool. "
        "Prioritize content from popular recipe websites. After identifying potential recipes, "
        "use the Web Scraper tool to extract relevant content. Employ the LLM to analyze, summarize, and synthesize findings, "
        "focusing on ingredients, cooking methods, variations, and cultural significance."
    ),
    decision_framework=(
        "1. Conduct an initial search to gather a wide range of recipe sources.\n"
        "2. Filter and prioritize recipes based on uniqueness, popularity, and potential interest.\n"
        "3. Use memory to track findings and identify variations between different recipes.\n"
        "4. Utilize LLM for deeper analysis, summarization, and insight generation.\n"
        "5. Delegate specific tasks (e.g., detailed scraping, additional searches) to specialized tools when needed."
    ),
    personality=(
        "You are enthusiastic, knowledgeable about various cuisines, and always searching for new and exciting recipes. "
        "You balance a methodical approach with creativity, enabling you to discover unique and delicious dishes."
    ),
    feedback_loop_enabled=True,
    feedback_loop_details=(
        "1. Regularly evaluate the effectiveness of search strategies and refine them based on outcomes.\n"
        "2. Adjust the focus and parameters of subsequent searches based on findings and identified gaps.\n"
        "3. Collaborate with the recipe writer agent to align future research with content creation needs."
    )
)

writer_agent = Agent(
    role="Recipe Writer and Chef",
    goal=(
        "Transform research insights provided by the search agent into a compelling and easy-to-follow recipe. "
        "Your objective is to craft recipes that are clear, precise, and include all necessary steps and ingredients. "
        "Ensure that the recipe is accessible to a wide audience, from beginner to advanced cooks."
    ),
    verbose=True,
    memory=True,
    backstory=(
        "As an experienced chef and writer, you have a deep understanding of flavors, ingredients, and cooking techniques. "
        "You excel at writing recipes that are easy to follow and deliver delicious results. You aim to make cooking fun and accessible."
    ),
    llm=llm,
    allow_delegation=False,
    strategy=(
        "Utilize research outputs to identify key elements of the recipes, such as ingredients, cooking methods, and variations. "
        "Develop recipes by expanding on these elements, ensuring clarity, step-by-step instructions, and creative variations. "
        "Regularly reference the core findings from the search agent to maintain alignment with the original discoveries."
    ),
    content_guidelines=(
        "1. **Audience Focus**: Write for an audience interested in cooking, from beginners to advanced cooks.\n"
        "2. **Clarity**: Ensure the recipe is easy to understand, with clear and concise instructions.\n"
        "3. **Accuracy**: Include correct measurements, ingredient lists, and cooking times.\n"
        "4. **Creativity**: Provide creative tips, substitutions, and variations to enhance the recipe."
    ),
    creativity_mode=True,
    inspiration_sources=[
        "International cuisines, traditional dishes, modern cooking techniques, and food trends."
    ],
    personality=(
        "You are passionate about cooking and love sharing your knowledge with others. Your recipes are known for their simplicity, flavor, and versatility."
    ),
    feedback_loop_enabled=True,
    feedback_loop_details=(
        "1. Regularly analyze reader feedback to refine future recipes.\n"
        "2. Adapt content styles and techniques based on what resonates most with the audience.\n"
        "3. Collaborate with the search agent to align future content with new discoveries and recipe elements."
    )
)

# Validation Agent
validation_agent = Agent(
    role="Recipe Validator",
    goal=(
        "Review and validate the research and recipe outputs provided by the search and recipe writer agents. "
        "Determine if the findings and the recipe content are accurate, relevant, and easy to follow. "
        "If the results meet the criteria, approve the recipe for publication."
    ),
    verbose=True,
    memory=True,
    backstory=(
        "You are a meticulous culinary editor with a keen eye for detail, tasked with ensuring the quality of research "
        "and recipe content. Your job is to verify the accuracy, consistency, and clarity of all outputs."
    ),
    llm=llm,
    allow_delegation=True,
    validation_strategy=(
        "1. Review the findings from the search agent to check for accuracy, completeness, and relevance to the recipe topic.\n"
        "2. Examine the content generated by the recipe writer agent for clarity, ease of understanding, and adherence to the specified guidelines.\n"
        "3. If both outputs are validated, approve the recipe content.\n"
        "4. If any output fails validation, provide feedback and request revisions."
    ),
    criteria=(
        "1. **Accuracy**: Are the research findings and recipe instructions correct and relevant to the topic?\n"
        "2. **Clarity**: Is the recipe easy to follow, with clear steps and instructions?\n"
        "3. **Completeness**: Does the recipe include all necessary ingredients, measurements, and cooking steps?\n"
        "4. **Engagement**: Is the content engaging and does it inspire the audience to try the recipe?\n"
        "5. **Alignment**: Does the recipe align with the insights uncovered during research?"
    ),
    feedback_loop_enabled=True,
    feedback_loop_details=(
        "1. Provide feedback to the search and recipe writer agents on areas needing improvement.\n"
        "2. Track any changes and enhancements made by the agents.\n"
        "3. Repeat the validation process until the outputs are acceptable."
    )
)

# Title Agent
title_agent = Agent(
    role="Recipe Title Generator",
    goal=(
        "Generate a compelling and descriptive title for the recipe based on its content. "
        "The title should be clear, concise, and attract the target audience."
    ),
    verbose=True,
    memory=False,
    backstory=(
        "You have an excellent sense for crafting engaging titles that capture the essence of any recipe. "
        "Your goal is to create a title that draws readers in while accurately reflecting the recipe's key attributes."
    ),
    llm=llm,
    allow_delegation=False,
    strategy=(
        "Analyze the main ingredients, cooking methods, and unique aspects of the recipe. Combine these insights to craft a title "
        "that is both enticing and descriptive."
    ),
)

# Research Task for Recipes
research_task = Task(
    description=(
        "Conduct an in-depth search to discover a variety of recipes related to the topic of '{topic}'. "
        "Your search should include:\n"
        "1. **Recipe Discovery**: Identify and retrieve recipes that are relevant to the topic. Focus on finding popular, unique, and interesting variations.\n"
        "2. **Recipe Analysis**: Analyze the identified recipes to extract key elements such as ingredients, cooking methods, and unique variations. Highlight any distinctive features or trends present in these recipes.\n"
        "3. **Summary and Insights**: Provide a summary of the most compelling recipes found. Include insights into what makes these recipes notable and how they fit into the broader context of the topic. Identify common ingredients or cooking techniques that emerge from the recipes.\n"
        "Ensure that your report is well-organized, with clear sections for recipe discovery, analysis, and summary. Use examples and details from the recipes where applicable to support your findings."
    ),
    expected_output=(
        "A well-structured report consisting of three sections:\n"
        "1. **Recipe Discovery**: A detailed list of identified recipes related to the topic, including their sources and a brief description.\n"
        "2. **Recipe Analysis**: An analysis of the recipes, covering key elements such as ingredients, cooking methods, and unique variations.\n"
        "3. **Summary and Insights**: A summary of the most compelling recipes with insights into their distinctive features, trends, and relevance to the topic."
    ),
    tools=[search_tool],
    agent=search_agent,
    async_execution=False,
)

# Writing Task for Recipes
write_task = Task(
    description=(
        "Develop a detailed recipe based on the research outputs provided by the search agent. "
        "Your recipe should include:\n"
        "1. **Ingredients**: A complete and accurate list of ingredients with measurements.\n"
        "2. **Instructions**: Clear and concise step-by-step cooking instructions.\n"
        "3. **Variations and Tips**: Creative suggestions for variations, substitutions, or additional cooking tips.\n"
        "Ensure that the recipe is accessible to a wide audience, with steps that are easy to follow and ingredients that are readily available."
        "Topic of recipe: {topic}\n"
        "Search Agent Findings: <p>{recipe_details}</p>"
        "Ensure the content is accurate, coherent, and engaging."
    ),
    expected_output=(
        "A comprehensive recipe document with the following sections:\n"
        "1. **Ingredients**: An accurate and complete list of ingredients with measurements.\n"
        "2. **Instructions**: Step-by-step cooking instructions that are clear and easy to follow.\n"
        "3. **Variations and Tips**: Suggestions for creative variations, substitutions, and additional cooking tips."
    ),
    agent=writer_agent,
    async_execution=False,
    output_file='temp-recipe.md'
)

# Validation Task for Recipes
validation_task = Task(
    description=(
        "Validate the research and recipe outputs provided by the search and recipe writer agents. "
        "Ensure that the research is accurate, comprehensive, and relevant, and that the recipe is clear, easy to follow, and meets the guidelines. "
        "Return a binary value: '1' if validation is successful and the content is correct, or '0' if validation fails. "
        "If validation is successful, ensure that the output only contains the binary value. "
        "If the output contains additional Markdown content or other information, process it accordingly, extracting only the validation result."
        "Topic of recipe: {topic}\n"
        "Findings of researcher agent: <p>{recipe_details}</p>\n"
        "Content of writer agent: <p>{recipe_content}</p>"
    ),
    expected_output="Binary value (0 or 1) indicating validation success or failure.",
    agent=validation_agent,
    async_execution=False,
)

# Title Generation Task for Recipes
title_task = Task(
    description=(
        "Based on the validated recipe written by write agent, generate the title of the recipe."
        "<recipe>{recipe_content}</recipe>"
        "Generate accurate title, do not add any files extension."
    ),
    expected_output="Just recipe title, with extraneous characters removed. Only alphanumeric characters.",
    agent=title_agent,
    async_execution=False,
    tools=[search_tool],
)

def generate_index():
    """Generate a unique index for log files."""
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def main(topic, retry_limit=3):
    """Main execution flow for recipe generation."""
    attempt = 0
    while attempt < retry_limit:
        try:
            # Researching
            research = Crew(
                tasks=[research_task],
                agents=[search_agent],
                tools=[search_tool],
            )
            recipe_details = research.kickoff(inputs={'topic': topic})  # Searching for recipes online

            # Writing
            write = Crew(
                tasks=[write_task],
                agents=[writer_agent],
            )
            recipe_content = write.kickoff(inputs={'topic': topic, 'recipe_details': recipe_details})  # Writing Recipe

            # Validation
            validation = Crew(
                tasks=[validation_task],
                agents=[validation_agent],
                tools=[search_tool],
            )
            validation_result = validation.kickoff(inputs={'topic': topic, 'recipe_details': recipe_details, 'recipe_content': recipe_content})
            print(f"\n\n\n\n\n\n\n\n\n\n\nValidation result: {validation_result}, Type: {type(validation_result)}\n\n\n\n\n\n\n\n\n\n\n")

            # Title Generation
            title_generation = Crew(
                tasks=[title_task],
                agents=[title_agent],
            )

            if int(validation_result) == 1:
                title = title_generation.kickoff(inputs={'recipe_content': recipe_content})

                # Moving file to output path
                output_path = os.path.join(base_path, "data")
                os.rename("temp-recipe.md", f"{title}.md")
                shutil.move(os.path.join(base_path, f"{title}.md"), os.path.join(output_path, f"{title}.md"))
                print(f"Recipe has been successfully saved as '{output_path}\\{title}.md'")
                break  # Exit loop if successful
            else:
                # Validation failed, log the issue
                logs_path = os.path.join(base_path, "logs")
                index = generate_index()
                shutil.move("temp-recipe.md", os.path.join(logs_path, f"{index}.md"))
                print(f"Logs saved at {logs_path} with file name {index}.md")
                print("Validation failed, re-running agents...")
                attempt += 1
        except Exception as e:
            print(f"An error occurred: {e}")
            attempt += 1
            if attempt >= retry_limit:
                print("Max retries reached. Process terminated.")

if __name__ == "__main__":
    # Getting recipe topic as input from the user
    topic = input("Enter a recipe topic: ")
    main(topic)