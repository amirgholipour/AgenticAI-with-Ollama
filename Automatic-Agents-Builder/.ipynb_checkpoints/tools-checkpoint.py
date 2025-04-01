
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


from crewai import Agent, Task, Crew, Process, LLM

from dotenv import load_dotenv

# --- Environment and Configuration ---

# Load environment variables (e.g., for API keys if using hosted models)
load_dotenv('creds.env')

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

