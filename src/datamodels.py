from dataclasses import dataclass


@dataclass
class Witness:
    work_url: str
    document_url: str
    pages: str
    siglum: str


@dataclass
class Document:
    url: str
    exemplar: str
    date: str
    language_principal: str


@dataclass
class ExternalLink:
    link: str
    source: str


@dataclass
class Work:
    url: str
    title: str
    author: str
    incipit: str
    form: str
    date: str
    language: str
    n_verses: int
    meter: str
    rhyme_scheme: str
    scripta: str
    keyword_p0: str
    keyword_p1: str
    keyword_e2: str
