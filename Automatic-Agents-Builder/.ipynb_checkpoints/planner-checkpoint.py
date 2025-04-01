import json
import os
from typing import List, Dict, Any, Optional
import yaml
import pickle
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool
from langchain_community.document_loaders import UnstructuredImageLoader
# If using OpenAI for planning or workers, uncomment the line below
# from langchain_openai import ChatOpenAI
from pydantic import Field, BaseModel, ConfigDict
from dotenv import load_dotenv

# --- Environment and Configuration ---

# Load environment variables (e.g., for API keys if using hosted models)
load_dotenv('creds.env')

# Configure LLMs (Using Ollama based on previous preference)
# Ensure Ollama server is running (e.g., `ollama serve`)
# Ensure required models are pulled (e.g., `ollama pull llama3:instruct`, `ollama pull gemma2:9b`)
OLLAMA_BASE_URL = "http://localhost:11434"
PLANNER_MODEL = "ollama/mistral-small:24b" # Model good for planning and JSON output - mistral-small:24b phi4:latest

try:
    # Planner LLM - Used to generate the crew plan
    planner_llm = LLM(model=PLANNER_MODEL, api_base=OLLAMA_BASE_URL)
    print(f"Planner LLM ({PLANNER_MODEL}) initialized.")



except Exception as e:
    print(f"Error initializing LLMs: {e}")
    print("Please ensure your LLM service (Ollama server or OpenAI key) is configured correctly.")
    exit()

# --- Tool Definitions ---

class TextExtractionTool(BaseTool):
    name: str = "Text Extraction Tool"
    description: str = (
        "Extracts readable text content from an image file. "
        "Input must be the path to the image file as a single string argument." # Be explicit
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # REMOVE Class-level Field if any was added back

    def _run(self, image_path: str) -> str: # The signature defines the expected arg
        if not isinstance(image_path, str) or not image_path:
             return "Error: Valid image path string was not provided to the tool."
        print(f"--- Running Text Extraction Tool on: {image_path} ---")
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
    description: str = (
        "Analyzes an image file and describes object positions and layout. "
        "Input must be the path to the image file as a single string argument." # Be explicit
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # REMOVE Class-level Field if any was added back

    def _run(self, image_path: str) -> str: # The signature defines the expected arg
        if not isinstance(image_path, str) or not image_path:
             return "Error: Valid image path string was not provided to the tool."
        print(f"--- Running Object Location Tool on: {image_path} ---")
        # Simulation remains the same
        return (f"Simulated analysis: Found standard UI elements (buttons, text areas, lists) "
                f"arranged in a typical application layout in image: {image_path}")

# --- Available Tools Registry ---
# Instantiate tools ONCE. They will be selected by the planner.
text_tool_instance = TextExtractionTool()
location_tool_instance = ObjectLocationTool()

AVAILABLE_TOOLS = {
    text_tool_instance.name: text_tool_instance,
    location_tool_instance.name: location_tool_instance
    # Add more tools here as needed
}

def get_tool_descriptions() -> str:
    """Returns a string describing available tools for the planner."""
    return "\n".join([f"- {name}: {tool.description}" for name, tool in AVAILABLE_TOOLS.items()])

# --- Dynamic Agent and Task Planning ---

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



def export_plan_to_yaml_and_pickle(crew_plan: CrewPlan, config_dir: str = "config"):
    # Ensure config directory exists
    os.makedirs(config_dir, exist_ok=True)

    # --- Prepare agents.yaml ---
    agents_yaml = {}
    for agent in crew_plan.agents:
        key = agent.role.lower().replace(" ", "_")
        agents_yaml[key] = {
            "role": agent.role,
            "goal": agent.goal,
            "backstory": agent.backstory,
            "assigned_tool_names": agent.assigned_tool_names
        }

    # --- Prepare tasks.yaml ---
    tasks_yaml = {}
    for task in crew_plan.tasks:
        key = task.name.lower().replace(" ", "_")
        agent_key = task.agent_role.lower().replace(" ", "_")
        tasks_yaml[key] = {
            "description": task.description.replace('{', '{').replace('}', '}'),
            "expected_output": task.expected_output,
            "agent": agent_key,
            "context_task_names": task.context_task_names
        }

    # --- Write to YAML files ---
    with open(os.path.join(config_dir, "agents.yaml"), "w") as af:
        yaml.dump(agents_yaml, af, sort_keys=False, allow_unicode=True)

    with open(os.path.join(config_dir, "tasks.yaml"), "w") as tf:
        yaml.dump(tasks_yaml, tf, sort_keys=False, allow_unicode=True)

    # --- Save full CrewPlan as a pickle file ---
    with open(os.path.join(config_dir, "crew_plan.pkl"), "wb") as pf:
        pickle.dump(crew_plan, pf)

    print("✅ Plan exported to config directory:")
    print(f"  - agents.yaml")
    print(f"  - tasks.yaml")
    print(f"  - crew_plan.pkl")



def create_crew_plan(user_goal: str, supporting_data: Dict[str, Any]) -> Optional[CrewPlan]:
    """
    Uses the Planner LLM to create a plan (agents and tasks) based on the user goal and available data/tools.
    """
    tool_descriptions = get_tool_descriptions()
    # Describe the *keys* available in supporting_data for placeholder usage
    data_keys_description = ", ".join(f"'{key}'" for key in supporting_data.keys())

    prompt = f"""
    Analyze the following user request and available resources to create a plan for a team of AI agents (a Crew).
    Your goal is to break down the user's request into specific, manageable tasks and assign them to specialized agents.

    User Request: "{user_goal}"

    Available Tools:
    {tool_descriptions if tool_descriptions else "No specific tools available."}

    Supporting Data Keys Provided (Available for use as placeholders like {{key_name}} in task descriptions):
    {data_keys_description if data_keys_description else "No specific data provided."}

    Instructions:
    1.  Define the necessary agents. Each agent should have a unique `role`, a clear `goal`, a brief `backstory`, and optionally `assigned_tool_names` from the Available Tools list. Only assign tools relevant to the agent's goal.
    2.  Define the tasks required to achieve the user request. Each task must have a unique `name`, a detailed `description`, the `expected_output`, the `agent_role` who will perform it, and `context_task_names` (a list of task names that must be completed before this task can start).
    3.  Ensure the tasks logically flow towards the final goal. The final task should synthesize the results.
    4.  **Crucially:** If a task needs to use data associated with a specific key (like 'image_path'), its `description` **must include the placeholder exactly like this: {{image_path}}**. Do NOT insert the actual value yourself; the system will substitute it later. For example: "Extract text from the image located at {{image_path}} using the Text Extraction Tool."
    5.  Output the plan ONLY as a valid JSON object adhering strictly to the following structure. Do not include ```json markdown or any other text outside the JSON structure itself.
        {{
          "agents": [
            {{
              "role": "Unique Role Name",
              "goal": "Specific goal for this agent",
              "backstory": "Brief relevant backstory",
              "assigned_tool_names": ["Tool Name 1", "Tool Name 2"]
            }}
          ],
          "tasks": [
            {{
              "name": "unique_task_name_1",
              "description": "Detailed description, possibly including placeholders like {{image_path}}",
              "expected_output": "Clear description of what this task should produce",
              "agent_role": "Unique Role Name",
              "context_task_names": []
            }},
            {{
              "name": "unique_task_name_2",
              "description": "Another task description",
              "expected_output": "Expected result",
              "agent_role": "Another Unique Role Name",
              "context_task_names": ["unique_task_name_1"]
            }}
          ]
        }}

    Respond ONLY with the JSON object.
    """

    print("--- Sending Request to Planner LLM ---")
    # print(f"Planner Prompt:\n{prompt}") # Uncomment for debugging

    try:
        # Use .invoke() for LangChain compatibility or direct call if using crewai LLM wrapper directly
        # Adjust based on the exact LLM object type
        if hasattr(planner_llm, 'invoke'):
             response = planner_llm.invoke(prompt)
             response_content = response.content # Assuming LangChain structure
        else:
             # Assuming CrewAI LLM wrapper might return string directly or need another method
             response = planner_llm.call(prompt) # Or appropriate method for CrewAI LLM
             response_content = str(response)

        response_content = response_content.strip()

        # Basic cleaning for potential markdown ```json fences
        if response_content.startswith("```json"):
            response_content = response_content[7:]
        if response_content.endswith("```"):
            response_content = response_content[:-3]
        response_content = response_content.strip()

        print("--- Planner LLM Raw Response ---")
        print(response_content)

        # Parse the JSON response using Pydantic models for validation
        plan_dict = json.loads(response_content)
        crew_plan = CrewPlan(**plan_dict)
        print("--- Crew Plan Parsed Successfully ---")
        export_plan_to_yaml_and_pickle(crew_plan, config_dir="config")  # <- CALL HERE
        return None

    except json.JSONDecodeError as e:
        print(f"\nError: Failed to decode JSON response from planner LLM: {e}")
        print(f"LLM Raw Response was:\n{response_content}")
        return None
    except Exception as e:
        print(f"\nError during planning phase: {e}")
        print(f"LLM Raw Response was likely:\n{response_content}") # Print response even on non-JSON errors
        return None
