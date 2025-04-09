import os
import yaml
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from main.types import BookOutline

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

@CrewBase
class OutlineCrew:
    """Book Outline Crew"""

    def __init__(self):
        agents_config = "config/agents.yaml"
        tasks_config = "config/tasks.yaml"

        self.llm = LLM(
            model=MODEL_NAME,
            api_base=OLLAMA_BASE_URL,
            timeout=1200,
            temperature=0.1,
            max_tokens=32000
        )

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],
            tools=[SerperDevTool()],
            llm=self.llm,
            verbose=True
        )

    @agent
    def outliner(self) -> Agent:
        return Agent(
            config=self.agents_config["outliner"],
            llm=self.llm,
            verbose=True
        )

    @task
    def research_topic(self) -> Task:
        return Task(config=self.tasks_config["research_topic"])

    @task
    def generate_outline(self) -> Task:
        return Task(
            config=self.tasks_config["generate_outline"],
            output_pydantic=BookOutline
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
