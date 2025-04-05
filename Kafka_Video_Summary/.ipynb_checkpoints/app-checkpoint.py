import streamlit as st
from video_processor import process_video

st.title("Video Processing with Kafka and Ollama")

uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    st.video(uploaded_file)
    if st.button("Process Video"):
        with st.spinner("Processing video..."):
            result = process_video(uploaded_file)
            st.success("✅ Video processed successfully!")
            st.subheader("📋 Video Summary")
            st.write(result)
