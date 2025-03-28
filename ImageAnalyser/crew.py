
import os
import yaml
from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool
from langchain_community.document_loaders import UnstructuredImageLoader
from pydantic import Field


# Define LLMs
llms = {
    "gemma": LLM(model="ollama/gemma3:12b", api_base="http://localhost:11434"),
    "granite_v": LLM(model="ollama/granite3.2-vision:latest", api_base="http://localhost:11434"),
    "granite": LLM(model="ollama/granite3.2:8b", api_base="http://localhost:11434"),
    "phi": LLM(model="ollama/phi4:latest", api_base="http://localhost:11434")
}

# ----------- Custom Tools -----------
class TextExtractionTool(BaseTool):
    name: str = "Text Extraction Tool"
    description: str = "Extracts readable text content from the image."
    image_path: str = Field(..., description="Path to the image file.")

    def _run(self) -> str:
        try:
            loader = UnstructuredImageLoader(self.image_path, mode="elements")
            documents = loader.load()
            extracted_texts = [doc.page_content for doc in documents]
            return "\n".join(extracted_texts) if extracted_texts else "No text found."
        except Exception as e:
            return f"Error extracting text: {str(e)}"

class ObjectLocationTool(BaseTool):
    name: str = "Object Location Tool"
    description: str = "Analyzes the image and describes object positions and layout."
    image_path: str = Field(..., description="Path to the image file.")

    def _run(self) -> str:
        return f"Simulated analysis of object positions in image: {self.image_path}"

# ----------- Helper Functions -----------
def load_yaml(filepath: str):
    with open(filepath, 'r') as file:
        return yaml.safe_load(file)

# ----------- Load Configurations -----------
agents_config = load_yaml('config/agents.yaml')
tasks_config = load_yaml('config/tasks.yaml')

# ----------- Initialize Agents from YAML -----------
agents = {}
for agent_name, config in agents_config.items():
    tools = []
    for tool_name in config.get('tools', []):
        if tool_name == "TextExtractionTool":
            tools.append(TextExtractionTool(image_path=""))
        elif tool_name == "ObjectLocationTool":
            tools.append(ObjectLocationTool(image_path=""))

    agents[agent_name] = Agent(
        role=config['role'],
        goal=config['goal'],
        backstory=config['backstory'],
        tools=tools,
        llm=llms[config['llm']],
        memory=True,
        respect_context_window=True,
        allow_delegation=config.get('allow_delegation', True),
        max_rpm=config.get('max_rpm', None),
        verbose=True
    )

# ----------- Initialize Tasks from YAML -----------
def initialize_tasks(image_path: str):
    tasks = []
    for task_conf in tasks_config:
        agent = agents[task_conf['agent']]
        for tool in agent.tools:
            tool.image_path = image_path

        task = Task(
            description=task_conf['description'],
            expected_output=task_conf['expected_output'],
            agent=agent
        )
        tasks.append(task)
    return tasks

# ----------- Crew Flow -----------
def process_image(image_path: str):
    tasks = initialize_tasks(image_path)
    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        verbose=True,
        max_iterations=10,  # ⛔ Prevent infinite loops
        embedder={
            "provider": "ollama",
            "config": {"model": "mxbai-embed-large"}
        }
    )
    result = crew.kickoff()
    return {
            "tasks_output": [task.output.__dict__ for task in crew.tasks],
            "token_usage": str(crew.usage_metrics),}
