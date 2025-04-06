from dotenv import load_dotenv
from textwrap import dedent
from crewai import Agent, Task, Crew, LLM
from tools import scrape_linkedin_posts_tool
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from tools.utils import load_yaml_file
import os

load_dotenv()



# Get values from .env
MODEL_NAME = os.getenv("MODEL_NAME")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")  # Or your desired token limit)  # Optional fallback

tool_mapping = {
    "scrape_linkedin_posts_tool": scrape_linkedin_posts_tool,
    "scrape_website_tool": ScrapeWebsiteTool(),
    "search_tool": SerperDevTool()
}

ollama_llm = LLM(model=MODEL_NAME, api_base=OLLAMA_BASE_URL, timeout=1200, temperature=0.1, max_tokens=32000)

def run_crew(topic: str, tone: str = "Neutral", persona: str = "Data Scientist") -> str:
    agent_defs = load_yaml_file("config/agents.yaml")
    task_defs = load_yaml_file("config/tasks.yaml")

    context = {
        "{{topic}}": topic,
        "{{tone}}": tone,
        "{{persona}}": persona
    }

    def apply_context(template: str):
        for key, value in context.items():
            template = template.replace(key, value)
        return dedent(template)

    # Create agents
    agents = {}
    for name, config in agent_defs.items():
        agents[name] = Agent(
            role=config["role"],
            goal=apply_context(config["goal"]),
            backstory=apply_context(config["backstory"]),
            tools=[tool_mapping[t] for t in config.get("assigned_tool_names", [])],
            verbose=True,
            allow_delegation=False,
            llm=ollama_llm
        )

    # Create tasks
    tasks = {}
    for name, config in task_defs.items():
        task = Task(
            description=apply_context(config["description"]),
            expected_output=apply_context(config["expected_output"]),
            agent=agents[config["agent"]],
        )
        tasks[name] = task

    # Set task context
    for name, config in task_defs.items():
        if config.get("context_task_names"):
            tasks[name].context = [tasks[ctx] for ctx in config["context_task_names"]]

    # Run crew
    crew = Crew(agents=list(agents.values()), tasks=list(tasks.values()))
    result = crew.kickoff()
    return result
