from dataclasses import dataclass


@dataclass
class Witness:
    href: str
    author: str
    title: str
    pages: str
    manuscript_url: str


@dataclass
class Manuscript:
    url: str
    exemplar: str
    date: str
    language_principal: str


@dataclass
class ExternalLink:
    link: str
    source: str
