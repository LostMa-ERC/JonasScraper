import lxml.html
import ural
from pydantic import BaseModel

from src.database.connection import Connection
from src.models.manuscript import Manuscript
from src.models.work import Work
from src.scrapers.manuscript import (
    ManuscriptScraper,
    iterate_witnesses_from_document,
)
from src.scrapers.utils import parse_id
from src.scrapers.work import WorkScraper, iterate_witnesses_from_work


class Sorter:
    @staticmethod
    def parse_url(url: str) -> tuple[str | None, BaseModel | None]:
        url = ural.strip_protocol(url)
        id = parse_id(url)
        paths = ural.urlpathsplit(url)
        if "oeuvre" in paths:
            url_type = Work
        elif "manuscrit" in paths:
            url_type = Manuscript
        else:
            url_type = None
        return id, url_type

    def __init__(self, conn: Connection):
        self.conn = conn

    def manuscript_workflow(
        self,
        url: str,
        doc_id: str,
        doc_html: lxml.html.Element,
    ) -> None:
        content = ManuscriptScraper(url=url, html=doc_html)
        model = content.validate()
        self.conn.insert_model(table_name="Manuscript", data=model)
        wits = []
        for wit in iterate_witnesses_from_document(doc_id=doc_id, doc_html=doc_html):
            self.conn.insert_model(table_name="Witness", data=wit)
            wits.append(wit)
        return model, wits

    def work_workflow(
        self,
        url: str,
        work_id: str,
        work_html: lxml.html.Element,
    ) -> None:
        content = WorkScraper(url=url, html=work_html)
        model = content.validate()
        self.conn.insert_model(table_name="Work", data=model)
        wits = []
        for wit in iterate_witnesses_from_work(work_id=work_id, work_html=work_html):
            self.conn.insert_model(table_name="Witness", data=wit)
            wits.append(wit)
        return model, wits

    def __call__(self, url: str, html: lxml.html.Element) -> None:
        id, record_type = self.parse_url(url=url)
        if record_type == Work:
            return self.work_workflow(url=url, work_id=id, work_html=html)
        elif record_type == Manuscript:
            return self.manuscript_workflow(url=url, doc_id=id, doc_html=html)
