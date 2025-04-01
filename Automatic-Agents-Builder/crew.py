from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from typing import List, Dict
from pydantic import BaseModel
from crewai import LLM
from langchain_community.document_loaders import UnstructuredImageLoader
import os
import yaml
import pickle
from pydantic import Field, BaseModel, ConfigDict

# --- Tool Definitions ---
WORKER_MODEL = "ollama/gemma3:12b"      # Model for executing tasks
OLLAMA_BASE_URL = "http://localhost:11434"

try:
    worker_llm = LLM(model=WORKER_MODEL, api_base=OLLAMA_BASE_URL)
    print(f"Worker LLM ({WORKER_MODEL}) initialized.")
except Exception as e:
    print(f"Error initializing LLMs: {e}")
    print("Please ensure your LLM service (Ollama server or OpenAI key) is configured correctly.")
    exit()


# Pydantic models for structured output from the planner
class AgentDef(BaseModel):
    role: str
    goal: str
    backstory: str
    assigned_tool_names: List[str] = Field(default_factory=list) # Names from AVAILABLE_TOOLS

class TaskDef(BaseModel):
    name: str # Unique name for dependency tracking
    description: str # Can contain placeholders like {key_name}
    expected_output: str
    agent_role: str # Role of the agent assigned to this task
    context_task_names: List[str] = Field(default_factory=list) # Names of prerequisite tasks

class CrewPlan(BaseModel):
    agents: List[AgentDef]
    tasks: List[TaskDef]    

def load_plan_from_pickle(config_dir: str = "config") -> CrewPlan:
    with open(os.path.join(config_dir, "crew_plan.pkl"), "rb") as pf:
        return pickle.load(pf)
class TextExtractionTool(BaseTool):
    name: str = "Text Extraction Tool"
    description: str = "Extracts readable text content from an image file. Input must be the path to the image file."
    
    def _run(self, image_path: str) -> str:
        """Extract text content from the image."""
        if not isinstance(image_path, str) or not image_path:
            return "Error: Valid image path string was not provided to the tool."
        try:
            loader = UnstructuredImageLoader(image_path, mode="elements")
            documents = loader.load()
            extracted_text = "\n".join(doc.page_content for doc in documents if doc.page_content)
            return extracted_text if extracted_text else "No text found in the image."
        except FileNotFoundError:
            return f"Error: Image file not found at path: {image_path}"
        except Exception as e:
            return f"Error extracting text from {image_path}: {str(e)}"


class ObjectLocationTool(BaseTool):
    name: str = "Object Location Tool"
    description: str = "Analyzes an image file and describes object positions and layout. Input must be the path to the image file."
    
    def _run(self, image_path: str) -> str:
        """Analyze layout of key UI elements in the image."""
        if not isinstance(image_path, str) or not image_path:
            return "Error: Valid image path string was not provided to the tool."
        # Simulated analysis for now; use actual layout analysis logic if needed
        return f"Simulated analysis: Found standard UI elements in {image_path}."

# Instantiate tools
text_tool_instance = TextExtractionTool()
location_tool_instance = ObjectLocationTool()

# --- Available Tools Registry ---
AVAILABLE_TOOLS = {
    text_tool_instance.name: text_tool_instance,
    location_tool_instance.name: location_tool_instance
}


# --- Execute Task ---
def execute_task(agent: Agent, task: Task) -> str:
    """Execute the task using the provided agent."""
    tool = agent.tools[0]  # Assuming the agent has one tool assigned (for simplicity)
    task_input = task.description.format(**task.context)  # Format task description with context
    if isinstance(tool, BaseTool) and hasattr(tool, "_run"):
        return tool._run(task_input)  # Run the tool's method and return the result
    else:
        return f"Error: Tool {tool.name} does not have a '_run' method."

def load_plan_from_yaml(config_dir: str = "config") -> Dict:
    with open(os.path.join(config_dir, "agents.yaml"), "r") as af:
        agents = yaml.safe_load(af)

    with open(os.path.join(config_dir, "tasks.yaml"), "r") as tf:
        tasks = yaml.safe_load(tf)

    # Convert to CrewPlan-like JSON dict structure
    agent_list = []
    for agent_key, agent_data in agents.items():
        agent_list.append({
            "role": agent_data["role"],
            "goal": agent_data["goal"],
            "backstory": agent_data["backstory"],
            "assigned_tool_names": agent_data.get("assigned_tool_names", [])
        })

    task_list = []
    for task_key, task_data in tasks.items():
        task_list.append({
            "name": task_key,
            "description": task_data["description"],
            "expected_output": task_data["expected_output"],
            "agent_role": agents[task_data["agent"]]["role"],
            "context_task_names": task_data.get("context_task_names", [])
        })

    return {"agents": agent_list, "tasks": task_list}


def load_plan_from_yaml_v2(config_dir: str = "config") -> Dict:
    with open(os.path.join(config_dir, "agents.yaml"), "r") as af:
        agents = yaml.safe_load(af)

    with open(os.path.join(config_dir, "tasks.yaml"), "r") as tf:
        tasks = yaml.safe_load(tf)

    # Convert to CrewPlan-compatible dictionary
    agent_list = []
    for agent_key, agent_data in agents.items():
        agent_list.append({
            "role": agent_data["role"],
            "goal": agent_data["goal"],
            "backstory": agent_data["backstory"],
            "assigned_tool_names": agent_data.get("assigned_tool_names", [])
        })

    task_list = []
    for task_key, task_data in tasks.items():
        agent_key = task_data["agent"]
        if agent_key not in agents:
            raise KeyError(f"Agent key '{agent_key}' not found in agents.yaml.")
        task_list.append({
            "name": task_key,
            "description": task_data["description"],
            "expected_output": task_data["expected_output"],
            "agent_role": agents[agent_key]["role"],
            "context_task_names": task_data.get("context_task_names", [])
        })

    return {"agents": agent_list, "tasks": task_list}


# --- Execute Crew Plan ---
def execute_crew_plan(crew_plan: Dict, supporting_data: Dict) -> str:
    agents_dict = {}
    tasks_list = []
    results = []

    # 1. Instantiate Agents Dynamically based on the crew plan
    for agent_def in crew_plan["agents"]:
        agent_tools = []
        for tool_name in agent_def["assigned_tool_names"]:
            tool = AVAILABLE_TOOLS.get(tool_name)
            if tool:
                agent_tools.append(tool)

        try:
            agent = Agent(
                role=agent_def["role"],
                goal=agent_def["goal"],
                backstory=agent_def["backstory"],
                tools=agent_tools,
                llm=worker_llm,  # Use the pre-initialized worker LLM
                verbose=True,
            )
            agents_dict[agent_def["role"]] = agent
        except Exception as e:
            print(f"Error creating agent '{agent_def['role']}': {e}")

    # 2. Instantiate Tasks Dynamically based on the crew plan
    tasks_dict = {}
    for task_def in crew_plan["tasks"]:
        agent = agents_dict.get(task_def["agent_role"])
        if agent:
            # Ensure that context tasks are properly resolved
            task_context = [tasks_dict[context_task_name] for context_task_name in task_def["context_task_names"] if context_task_name in tasks_dict]

            # Format the task description with supporting data
            try:
                task_description = task_def["description"].format(**supporting_data)
            except KeyError as e:
                print(f"Error formatting description for task '{task_def['name']}': Missing key {e} in supporting_data.")
                continue  # Skip this task

            # Instantiate the task
            try:
                task = Task(
                    description=task_description,
                    expected_output=task_def["expected_output"],
                    agent=agent,
                    context=task_context if task_context else None,
                )
                tasks_list.append(task)
                tasks_dict[task_def["name"]] = task
            except Exception as e:
                print(f"Error creating task '{task_def['name']}': {e}")
                continue  # Skip this task

    # 3. Create the dynamic crew
    if agents_dict and tasks_list:
        dynamic_crew = Crew(
            agents=list(agents_dict.values()),
            tasks=tasks_list,
            verbose=True,  # Use level 2 for more detail
            process=Process.sequential  # Execute tasks sequentially
        )

        print("\n--- Kicking off Dynamically Created Crew ---")
        try:
            result = dynamic_crew.kickoff()  # This will run the tasks and return the result

            print("\n\n--- ========= Dynamic Crew Execution Result ========= ---")
            print(result)
            print("--- =================================================== ---")
            return result
        except Exception as e:
            print(f"\nAn error occurred during crew execution: {e}")
            import traceback
            traceback.print_exc()
            return f"Error: {e}"
    else:
        return "\nError: No valid agents or tasks were created based on the plan. Cannot run Crew."



# --- Main Execution Logic ---
if __name__ == "__main__":
    # Example user goal and supporting data
    user_goal = (
        "Analyze the provided image. "
        "First, extract all visible text content. "
        "Second, describe the spatial layout and positions of key UI elements. "
        "Finally, synthesize this information into a concise summary describing the board's structure and content."
    )

    supporting_data = {
        "image_path": "/Users/skasmani/Downloads/personal/github/AgenticAI-with-Ollama/ImageAnalyser/temp/citations.png"
    }

    # Step 1: Generate Crew Plan using Planner LLM
    # create_crew_plan(user_goal, supporting_data)
    crew_plan = load_plan_from_yaml(config_dir="config")
    # crew_plan = load_plan_from_pickle(config_dir="config").dict()

    # Step 2: Execute the plan only if the crew plan was generated successfully
    if crew_plan:
        print("\n--- Instantiating and Executing Dynamic Crew ---")
        result = execute_crew_plan(crew_plan.dict(), supporting_data)
        print(result)
    else:
        print("\nFailed to generate a crew plan. Cannot proceed.")
