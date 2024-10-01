# conda activate "D:\TanDoori Data\DataBase\Projects\AIDevelopment\Project 010 - Blog Writer Tool\blogWriter"

from crewai import Crew, Process
from tasks import research_task, write_task
from agents import news_researcher, news_writer

crew = Crew(
    tasks=[research_task,write_task],
    agents=[news_researcher,news_writer],
    process=Process.sequential,
)

result = crew.kickoff(inputs={'topic':"AI in Education"})
print(result)