import streamlit as st
from planner import create_crew_plan
from crew import execute_crew_plan, load_plan_from_yaml, load_plan_from_pickle
import urllib.parse

# Set up the Streamlit interface
st.title("ThinkPlanSolve")

st.write("**ThinkPlanSolve** is a dynamic AI task planner and executor powered by [CrewAI](https://github.com/joaomdmoura/crewAI), [Ollama](https://ollama.com/), and [Streamlit](https://streamlit.io/). It takes a user-defined problem or goal, uses a large language model (LLM) to break it down into agent roles and tasks, and executes them using a multi-agent CrewAI setup.")


# Input for user goal
user_request = st.text_area("Enter your User Ask:", 
                         "Analyze the provided image. "
                         "First, extract all visible text content. "
                         "Second, describe the spatial layout and positions of key UI elements. "
                         "Finally, synthesize this information into a concise and comprehensive summary describing the content in a professional way.")

# Input for image path (Make sure to upload an image or use a local file)
image_path = st.text_input("Enter path for supporting documents:", "/Users/skasmani/Downloads/personal/github/AgenticAI-with-Ollama/ImageAnalyser/temp/citations.png")


# Your original image path
image_path = "/Users/skasmani/Downloads/personal/github/AgenticAI-with-Ollama/ImageAnalyser/temp/citations.png"

# Use urllib to encode the path properly, especially handling spaces or special characters
image_path = urllib.parse.quote(image_path)
if st.button("Generate Crew Plan and Execute Tasks"):
    if image_path:
        supporting_data = {
            "image_path": image_path
        }

        # Generate Crew Plan
        create_crew_plan(user_goal, supporting_data)
        crew_plan = load_plan_from_yaml(config_dir="config")
        # crew_plan = load_plan_from_pickle(config_dir="config").dict()

        if crew_plan:
            # Execute the tasks and show the final result
            # result = execute_crew_plan(crew_plan.dict(), supporting_data)
            result = execute_crew_plan(crew_plan, supporting_data)
            st.write(f"--- Execution Result ---")
            st.text(result)  # Display the task execution result as text
        else:
            st.write("Failed to generate a valid Crew Plan.")
    else:
        st.write(f"Error: Image file not found at {image_path}. Please check the path.")
