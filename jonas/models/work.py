from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field


def join_list(value: list | None) -> str | None:
    if isinstance(value, list):
        return "|".join(value)


class Work(BaseModel):
    id: str
    title: str | None = Field(default=None)
    author: str | None = Field(default=None)
    incipit: str | None = Field(default=None)
    form: str | None = Field(default=None)
    date: str | None = Field(default=None)
    language: str | None = Field(default=None)
    n_verses: str | None = Field(default=None)
    meter: str | None = Field(default=None)
    rhyme_scheme: str | None = Field(default=None)
    scripta: str | None = Field(default=None)
    keywords: Annotated[str, BeforeValidator(join_list)] = Field(default=None)
    links: Annotated[str, BeforeValidator(join_list)] = Field(default=None)
