# planner_crew.py

import os
import yaml
import json
import re
from typing import Dict, Any
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool
from langchain_community.document_loaders import UnstructuredImageLoader
from pydantic import ConfigDict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('creds.env')

# --- LLM Configuration ---
OLLAMA_BASE_URL = "http://localhost:11434"
PLANNER_MODEL = "ollama/mistral-small:24b"  # You can switch to phi4:latest or others

try:
    planner_llm = LLM(model=PLANNER_MODEL, api_base=OLLAMA_BASE_URL)
    print(f"Planner LLM ({PLANNER_MODEL}) initialized.")
except Exception as e:
    raise RuntimeError(f"LLM init failed: {e}")

# --- Tool Definitions ---
class TextExtractionTool(BaseTool):
    name: str = "Text Extraction Tool"
    description: str = "Extracts readable text from an image file. Input must be a path string."
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, image_path: str) -> str:
        if not isinstance(image_path, str) or not image_path:
            return "Error: Valid image path string was not provided."
        try:
            loader = UnstructuredImageLoader(image_path, mode="elements")
            documents = loader.load()
            return "\n".join(doc.page_content for doc in documents if doc.page_content)
        except Exception as e:
            return f"Error extracting text: {str(e)}"

class ObjectLocationTool(BaseTool):
    name: str = "Object Location Tool"
    description: str = "Describes object positions in an image. Input must be a path string."
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, image_path: str) -> str:
        if not isinstance(image_path, str) or not image_path:
            return "Error: Valid image path string was not provided."
        return f"Simulated layout analysis for: {image_path}"

# --- Tool Registry ---
text_tool_instance = TextExtractionTool()
location_tool_instance = ObjectLocationTool()
AVAILABLE_TOOLS = {
    text_tool_instance.name: text_tool_instance,
    location_tool_instance.name: location_tool_instance
}

# Get tool descriptions to inject into agent prompts
def get_tool_descriptions() -> str:
    return "\n".join([f"- {name}: {tool.description}" for name, tool in AVAILABLE_TOOLS.items()])

# Load agent and task plans from YAML files
def load_yaml_plan(config_dir: str) -> Dict:
    with open(os.path.join(config_dir, "agents_planner.yaml"), 'r') as af:
        agents_yaml = yaml.safe_load(af)
    with open(os.path.join(config_dir, "tasks_planner.yaml"), 'r') as tf:
        tasks_yaml = yaml.safe_load(tf)
    return agents_yaml, tasks_yaml

# Inject tool descriptions into template text
def inject_tool_descriptions(text: str, tool_descriptions: str) -> str:
    return text.replace("{{tool_descriptions}}", tool_descriptions)

# Extract placeholders from a template string
def extract_placeholders(text: str):
    return re.findall(r"{(.*?)}", text)


# Clean markdown wrappers from LLM JSON output
def clean_json_output(raw_output: str) -> str:
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_output.strip(), flags=re.MULTILINE)

# Save raw JSON output as CrewAI-compatible YAML files
def save_crew_yaml_from_raw_json(raw_json: str, output_dir: str = "./config"):
    try:
        data = json.loads(raw_json)

        agents = data.get("agents", [])
        tasks = data.get("tasks", [])

        print(agents)
        print("****" * 30)
        print(tasks)

        # Convert agents
        agents_yaml = {}
        for agent in agents:
            key = agent["role"].lower().replace(" ", "_")
            agents_yaml[key] = {
                "role": agent["role"],
                "goal": agent["goal"],
                "backstory": agent["backstory"],
                "assigned_tool_names": agent.get("assigned_tool_names") or agent.get("tool_names", [])
            }

        # Convert tasks
        tasks_yaml = {}
        for task in tasks:
            key = task["name"].lower().replace(" ", "_")
            agent_role = task.get("agent_role")
            if not agent_role:
                print(f"⚠️ Warning: No agent_role found for task: {task.get('name', 'Unknown')}")
                agent_key = None
            else:
                agent_key = agent_role.lower().replace(" ", "_")

            tasks_yaml[key] = {
                "description": task["description"],
                "expected_output": task["expected_output"],
                "agent": agent_key,
                "context_task_names": task.get("context_task_names") or task.get("dependencies", [])
            }

        # Save files
        os.makedirs(output_dir, exist_ok=True)
        agents_path = os.path.join(output_dir, "agents.yaml")
        tasks_path = os.path.join(output_dir, "tasks.yaml")

        with open(agents_path, "w") as af:
            yaml.dump(agents_yaml, af, sort_keys=False, allow_unicode=True)

        with open(tasks_path, "w") as tf:
            yaml.dump(tasks_yaml, tf, sort_keys=False, allow_unicode=True)

        print(f"✅ YAML plan saved: {agents_path} and {tasks_path}")

    except json.JSONDecodeError:
        print("❌ Error: Could not decode JSON.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


# Main execution function
def execute_planning_crew(user_request: str, supporting_data: Dict[str, Any] = {}):
    # instruction = (
    #     "Important: Try to solve the user request using the minimum number of agents and tasks possible. "
    #     "Avoid redundancy. Do not exceed 8 total steps (including all tasks and agents), unless absolutely necessary."
    # )
    # user_goal_with_instruction = f"{user_goal}\n\n{instruction}"

    agents_yaml, tasks_yaml = load_yaml_plan(config_dir="config/")
    tool_descriptions = get_tool_descriptions()

    # Create agents from YAML
    agents = {}
    for key, agent_data in agents_yaml.items():
        goal = inject_tool_descriptions(agent_data["goal"], tool_descriptions)
        backstory = inject_tool_descriptions(agent_data["backstory"], tool_descriptions)
        tools = [AVAILABLE_TOOLS[name] for name in agent_data.get("assigned_tool_names", []) if name in AVAILABLE_TOOLS]
        agents[key] = Agent(
            role=agent_data["role"],
            goal=goal,
            backstory=backstory,
            tools=tools,
            llm=planner_llm,
            verbose=True
        )

    # Create tasks from YAML
    tasks = {}
    task_objs = []
    for key, task_data in tasks_yaml.items():
        agent_key = task_data["agent"]
        context = [tasks[name] for name in task_data.get("context_task_names", []) if name in tasks]
        full_context = {"user_request": user_request, **supporting_data}
        description = inject_tool_descriptions(task_data["description"], tool_descriptions)
        try:
            formatted_description = description.format(**full_context)
        except KeyError:
            formatted_description = description
        task = Task(
            description=formatted_description,
            expected_output=task_data["expected_output"],
            agent=agents[agent_key],
            context=context or None
        )
        tasks[key] = task
        task_objs.append(task)

    # Execute the crew sequentially
    crew = Crew(
        agents=list(agents.values()),
        tasks=task_objs,
        process=Process.sequential,
        verbose=True
    )

    print("\n🚀 Running Planner Crew to generate CrewPlan...")
    result = crew.kickoff()
    print("\n✅ Planner Crew Execution Result:\n", result)
    cleaned_output = clean_json_output(result.tasks_output[-2].raw)
    save_crew_yaml_from_raw_json(cleaned_output)
    return None

# --- Example Execution ---
if __name__ == "__main__":
    user_request = '''Analyze the provided image.
                  First, extract all visible text content. 
                  Second, describe the spatial layout and positions of key UI elements. 
                  Finally, synthesize this information into a concise summary describing the board's structure and content.'''
    supporting_data = {
        "image_path": "/Users/skasmani/Downloads/personal/github/AgenticAI-with-Ollama/ImageAnalyser/temp/Screenshot 2025-03-21 at 11.29.44 am.png"
    }
    result = execute_planning_crew(user_request, supporting_data)

    
