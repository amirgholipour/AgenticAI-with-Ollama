from typing import List

from pydantic import BaseModel
# from uuid import uuid4
# from pydantic import Field

# class BookState(BaseModel):
#     id: str = Field(default_factory=lambda: str(uuid4()))  # <- This line added

class ChapterOutline(BaseModel):
    # id: str = Field(default_factory=lambda: str(uuid4()))  # <- This line added
    title: str
    description: str


class BookOutline(BaseModel):
    # id: str = Field(default_factory=lambda: str(uuid4()))  # <- This line added
    chapters: List[ChapterOutline]


class Chapter(BaseModel):
    # id: str = Field(default_factory=lambda: str(uuid4()))  # <- This line added
    title: str
    content: str
