import streamlit as st
from crew import run_crew

st.set_page_config(page_title="LinkedIn Post Generator", layout="centered")

st.title("🚀 AI-Driven LinkedIn Post Generator")
st.caption("Craft high-quality, influencer-style posts based on any topic")

topic = st.text_input("🔍 Topic (e.g., 'Llama4')")

col1, col2 = st.columns(2)
with col1:
    persona = st.selectbox("🧠 Choose a persona:", ["AI Leader", "Data Scientist", "Product Manager", "CTO"])
with col2:
    tone = st.selectbox("🎭 Choose a tone:", ["Optimistic", "Neutral", "Bold"])

if st.button("Generate Post"):
    if not topic.strip():
        st.warning("Please enter a topic.")
    else:
        with st.spinner("🤖 Crafting your LinkedIn post..."):
            try:
                result = run_crew(topic=topic, tone=tone, persona=persona)
                st.success("✅ Post Ready!")
                st.markdown("### ✍️ Your LinkedIn Post")
                st.markdown(result)
            except Exception as e:
                st.error(f"Error occurred: {e}")
