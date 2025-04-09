from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from main.types import Chapter
import os
from dotenv import load_dotenv

load_dotenv()

# Get values from .env
MODEL_NAME = os.getenv("MODEL_NAME")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


@CrewBase
class WriteBookChapterCrew:
    """Write Book Chapter Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    llm = LLM(
        model=MODEL_NAME,
        api_base=OLLAMA_BASE_URL,
        timeout=1200,
        temperature=0.1,
        max_tokens=32000
    )

    # ------------------- AGENTS -------------------

    @agent
    def researcher(self) -> Agent:
        search_tool = SerperDevTool()
        return Agent(
            config=self.agents_config["researcher"],
            tools=[search_tool],
            llm=self.llm,
        )

    @agent
    def code_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["code_writer"],
            llm=self.llm,
            allow_code_execution=True
        )

    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config["writer"],
            llm=self.llm,
        )

    # ------------------- TASKS -------------------

    @task
    def research_chapter(self) -> Task:
        return Task(
            config=self.tasks_config["research_chapter"]
        )

    @task
    def generate_code(self) -> Task:
        return Task(
            config=self.tasks_config["generate_code"],
            context=[self.research_chapter()]
        )

    @task
    def write_chapter(self) -> Task:
        return Task(
            config=self.tasks_config["write_chapter"],
            output_pydantic=Chapter,
            context=[self.generate_code()]
        )

    # ------------------- CREW -------------------

    @crew
    def crew(self) -> Crew:
        """Creates the Write Book Chapter Crew"""
        return Crew(
            agents=[
                self.researcher(),
                self.code_writer(),
                self.writer()
            ],
            tasks=[
                self.research_chapter(),
                self.generate_code(),
                self.write_chapter()
            ],
            process=Process.sequential,
            verbose=True,
        )
