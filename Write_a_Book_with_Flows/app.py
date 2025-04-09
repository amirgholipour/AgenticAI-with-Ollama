import streamlit as st
import asyncio
from main.main import BookFlow, BookState

st.set_page_config(page_title="📚 AI Book Writer", layout="wide")
st.title("📘 Write a Book with CrewAI & Ollama")

# Input fields
title = st.text_input("Book Title", value="The Current State of AI in April 2025")
topic = st.text_area("Book Topic", value="Exploring the latest trends in AI across different industries.")
goal = st.text_area("Goal of the Book", height=200, value="""
The goal of this book is to provide a comprehensive overview of the current state of artificial intelligence in April 2025.
It will delve into the latest trends impacting various industries and analyze significant advancements.
""")
number_of_chapters = st.text_area("Number of chapters", value="2")
number_of_words = st.text_area("Number of words in each chapter", value="200")
# Trigger book writing flow
if st.button("Generate Book"):
    st.info("⏳ Running the book-writing crew flow...")
    with st.spinner("Crew is working..."):

        # Build the book state
        state = BookState(title=title, topic=topic, goal=goal, number_of_words=number_of_words,number_of_chapters=number_of_chapters)

        # Run the flow with the user-defined state
        flow = BookFlow(state)

        # Create an asyncio loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Run flow steps
        flow.generate_book_outline()
        loop.run_until_complete(flow.write_chapters())
        loop.run_until_complete(flow.join_and_save_chapter())

        # Display results
        st.success("✅ Book outline and chapters generated and saved!")

        
        for chapter in flow.state.book:
            st.subheader(chapter.title)
            st.text_area("Chapter Content", chapter.content, height=300)

