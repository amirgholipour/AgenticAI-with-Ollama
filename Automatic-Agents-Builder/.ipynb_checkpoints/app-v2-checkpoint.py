# At the top of your script
import os
os.environ["STREAMLIT_SERVER_RUN_ON_SAVE"] = "false"
import streamlit as st
from planner_crew import execute_planning_crew
from executer_crew import execute_crew_plan, load_plan_from_yaml
import urllib
# Set up the Streamlit interface
# st.title("ThinkPlanSolve")
st.markdown("<h1 style='text-align: center;'>ThinkPlanSolve</h1>", unsafe_allow_html=True)


st.write("**ThinkPlanSolve** is a dynamic AI task planner and executor powered by [CrewAI](https://github.com/joaomdmoura/crewAI), [Ollama](https://ollama.com/), and [Streamlit](https://streamlit.io/). It takes a user-defined problem or goal, uses a large language model (LLM) to break it down into agent roles and tasks, and executes them using a multi-agent CrewAI setup.")


# Input for user goal
user_request = st.text_area("Enter your User Ask:", 
                         "Analyze the provided image. "
                         "First, extract all visible text content. "
                         "Second, describe the spatial layout and positions of key UI elements. "
                         "Finally, share your understanding about the provided image.")

# Input for image path (Make sure to upload an image or use a local file)
image_path = st.text_input("Enter path for supporting documents:", "/Users/skasmani/Downloads/personal/github/AgenticAI-with-Ollama/ImageAnalyser/temp/citations.png")


# Use urllib to encode the path properly, especially handling spaces or special characters
# image_path = urllib.parse.quote(image_path)
if st.button("Generate Crew Plan and Execute Tasks"):
    if image_path:
        supporting_data = {
            "image_path": image_path
        }

        # Generate Crew Plan
        execute_planning_crew(user_request, supporting_data)
        
        crew_plan = load_plan_from_yaml(config_dir="config")

        if crew_plan:
            # Execute the tasks and show the final result
            # result = execute_crew_plan(crew_plan.dict(), supporting_data)
            executer_result = execute_crew_plan(crew_plan, supporting_data)
            st.write(f"--- Execution Result ---")
            # If it's a plain string (like in your example), just use st.markdown with formatting
            st.markdown("### 📝 Final Summary of Image Analysis")
            st.success(executer_result)
            
            # Optionally, use expandable details if the result grows longer:
            with st.expander("📄 View Full Analysis Details"):
                st.write(executer_result)
        else:
            st.write("Failed to generate a valid Crew Plan.")
    else:
        st.write(f"Error: Image file not found at {image_path}. Please check the path.")
