from pydantic import BaseModel, Field


class Manuscript(BaseModel):
    id: str
    exemplar: str | None = Field(default=None)
    date: str | None = Field(default=None)
    language: str | None = Field(default=None)
