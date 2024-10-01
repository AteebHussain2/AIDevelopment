from crewai import Task
from tools import tool
from agents import news_researcher, news_writer

# Research Task

research_task = Task(
    description = (
        "Identify the next big trend in {topic}."
        "Focus on identifying pros and cons and the overall narrative"
        "Your final report should clearly articulate the key points, its market opportunities and potential risks."
    ),
    expected_output = "A comprehensive 3 paragraphs long report on latest AI trends",
    tools = [tool],
    agent = news_researcher,
)

# write Task

write_task = Task(
    description = (
        "Compose an insightful article on {topic}."
        "Focus on latet trends and how its impacting the industry"
        "This article should be easy to understand, engaging and positive"
    ),
    expected_output = "A 4 paragraphs article on {topic} advancemnets formatd as markdown",
    tools = [tool],
    agent = news_writer,
    async_execution = False,
    output_file = 'blog-post.md'
)