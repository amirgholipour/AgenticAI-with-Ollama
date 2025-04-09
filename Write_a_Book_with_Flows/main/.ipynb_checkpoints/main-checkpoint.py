#!/usr/bin/env python
import asyncio
from typing import List

from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel

# from write_a_book_with_flows.crews.write_book_chapter_crew.write_book_chapter_crew import (
#     WriteBookChapterCrew,
# )
# from write_a_book_with_flows.types import Chapter, ChapterOutline

# from .crews.outline_book_crew.outline_crew import OutlineCrew


from crews.outline_crew.outline_crew import OutlineCrew
from crews.chapter_crew.write_book_chapter_crew import WriteBookChapterCrew
from main.types import Chapter, ChapterOutline
from uuid import uuid4
from pydantic import Field


class BookState(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))  # <- This line added
    title: str = "The Current State of AI in April 2023"
    book: List[Chapter] = []
    book_outline: List[ChapterOutline] = []
    topic: str = (
        "Exploring the latest trends in AI across different industries as of April 2025"
    )
    goal: str = """
        The goal of this book is to provide a comprehensive overview of the current state of artificial intelligence in April 2025.
        It will delve into the latest trends impacting various industries, analyze significant advancements,
        and discuss potential future developments. The book aims to inform readers about cutting-edge AI technologies
        and prepare them for upcoming innovations in the field.
    """
    number_of_words: str ="3000"
    number_of_chapters: str ="2"


class BookFlow(Flow[BookState]):
    id: str = Field(default_factory=lambda: str(uuid4()))

    def __init__(self, state: BookState):
        self.initial_state = state  # ✅ THIS is allowed
        super().__init__()

    @start()
    def generate_book_outline(self):
        print("Kickoff the Book Outline Crew")
        print(self.state.number_of_words)
        output = (
            OutlineCrew()
            .crew()
            .kickoff(inputs={"topic": self.state.topic, "goal": self.state.goal, "number_of_chapters": self.state.number_of_chapters, "number_of_words": self.state.number_of_words })
        )

        chapters = output["chapters"]
        print("Chapters:", chapters)

        self.state.book_outline = chapters
        return chapters

    @listen(generate_book_outline)
    async def write_chapters(self):
        print("Writing Book Chapters")
        tasks = []

        async def write_single_chapter(chapter_outline):
            output = (
                WriteBookChapterCrew()
                .crew()
                .kickoff(
                    inputs={
                        "goal": self.state.goal,
                        "topic": self.state.topic,
                        "number_of_words": self.state.number_of_words,
                        "chapter_title": chapter_outline.title,
                        "chapter_description": chapter_outline.description,
                        "book_outline": [
                            chapter_outline.model_dump_json()
                            for chapter_outline in self.state.book_outline
                        ],
                    }
                )
            )
            title = output["title"]
            content = output["content"]
            chapter = Chapter(title=title, content=content)
            return chapter

        for chapter_outline in self.state.book_outline:
            print(f"Writing Chapter: {chapter_outline.title}")
            print(f"Description: {chapter_outline.description}")
            task = asyncio.create_task(write_single_chapter(chapter_outline))
            tasks.append(task)

        chapters = await asyncio.gather(*tasks)
        self.state.book.extend(chapters)
        print("Book Chapters", self.state.book)

    @listen(write_chapters)
    async def join_and_save_chapter(self):
        print("Joining and Saving Book Chapters")
        book_content = ""

        for chapter in self.state.book:
            book_content += f"# {chapter.title}\n\n{chapter.content}\n\n"
        print("****"*30)
        book_title = self.state.title
        print(book_title)
        print("****"*30)
        filename = f"./{book_title.replace(' ', '_')}.md"
        print("before")
        with open(filename, "w", encoding="utf-8") as file:
            file.write(book_content)

        print("after")
        print(f"Book saved as {filename}")
        return book_content




def kickoff():
    poem_flow = BookFlow()
    poem_flow.kickoff()


def plot():
    poem_flow = BookFlow()
    poem_flow.plot()


if __name__ == "__main__":
    kickoff()
    plot()
