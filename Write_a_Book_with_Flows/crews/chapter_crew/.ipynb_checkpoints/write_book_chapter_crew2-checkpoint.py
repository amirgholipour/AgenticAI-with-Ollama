from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
# from langchain_openai import ChatOpenAI

from main.types import Chapter
import os
from dotenv import load_dotenv

load_dotenv()



# Get values from .env
MODEL_NAME = os.getenv("MODEL_NAME")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")  # Or your desired token limit)  # Optional fallback




@CrewBase
class WriteBookChapterCrew:
    """Write Book Chapter Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    # llm = ChatOpenAI(model="gpt-4o")
    llm = LLM(model=MODEL_NAME, api_base=OLLAMA_BASE_URL, timeout=1200, temperature=0.1, max_tokens=32000)


    @agent
    def researcher(self) -> Agent:
        search_tool = SerperDevTool()
        return Agent(
            config=self.agents_config["researcher"],
            tools=[search_tool],
            llm=self.llm,
        )

    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config["writer"],
            llm=self.llm,
        )

    @task
    def research_chapter(self) -> Task:
        return Task(
            config=self.tasks_config["research_chapter"],
        )

    @task
    def write_chapter(self) -> Task:
        return Task(config=self.tasks_config["write_chapter"], output_pydantic=Chapter)

    @crew
    def crew(self) -> Crew:
        """Creates the Write Book Chapter Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
