from typing import List

from pydantic import BaseModel, Field


class WorkModel(BaseModel):
    id: str
    title: str
    author: str | None = Field(default=None)
    incipit: str | None = Field(default=None)
    form: str | None = Field(default=None)
    date: str | None = Field(default=None)
    language: str | None = Field(default=None)
    n_verses: str | None = Field(default=None)
    meter: str | None = Field(default=None)
    rhyme_scheme: str | None = Field(default=None)
    scripta: str | None = Field(default=None)
    keywords: List[str | None] = Field(default=[])
    links: List[str | None] = Field(default=[])
