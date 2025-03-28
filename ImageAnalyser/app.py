import streamlit as st
from crew import process_image
import os
import json
st.set_page_config(page_title="AI Image Analysis Assistant", layout="centered")

st.title("🧠 AI Image Insight Assistant")
st.markdown("Upload an image and let our senior AI agents analyze its content and layout.")

uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image_path = os.path.join("temp", uploaded_file.name)
    os.makedirs("temp", exist_ok=True)
    with open(image_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.image(image_path, caption="Uploaded Image", use_column_width=True)
    st.write("Analyzing image...")

    result = process_image(image_path)
    st.success("Analysis Complete!")
    st.markdown("### 📝 Summary")
    
    
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except Exception:
            st.write("❌ Unable to parse result.")
            st.stop()
    
    if "tasks_output" in result:
        st.markdown("### ✅ Detailed Analysis")
        for i, task in enumerate(result["tasks_output"]):
            st.markdown(f"#### 🔹 Task {i+1}: {task.get('description', 'Unnamed Task')}")
            st.markdown(f"**Agent:** {task.get('agent', 'N/A')}")
    
            raw_output = task.get("raw", "")
            if raw_output.strip().startswith("```json"):
                st.markdown("**Output:**")
                st.code(raw_output, language="json")
            else:
                st.markdown("**Output:**")
                st.markdown(raw_output)
    else:
        st.warning("No structured task output available.")
    

    # st.write(result)
