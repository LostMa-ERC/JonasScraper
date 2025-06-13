from pydantic import BaseModel, Field


class Witness(BaseModel):
    id: str
    doc_id: str
    work_id: str
    date: str | None = Field(default=None)
    siglum: str | None = Field(default=None)
    status: str | None = Field(default=None)
    foliation: str | None = Field(default=None)
