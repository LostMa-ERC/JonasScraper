from typing import Generator

from jonas.models.witness import Witness
from jonas.parsers.utils import Table
from jonas.utils import parse_id
from lxml import html


def iterate_witnesses_from_document(
    doc_id: str,
    doc_html: html.Element,
    doc_date: str | None = None,
) -> Generator[Witness, None, None]:
    for block in doc_html.xpath("//div[@class='un_temoin']"):
        wit = ManuscriptWitnessScraper(doc_id=doc_id, block=block, date=doc_date)
        model = wit.model()
        yield model


class ManuscriptWitnessScraper:
    def __init__(self, doc_id: str, block: html.Element, date: str | None):
        self.doc_id = doc_id
        self._html = block
        self._details = self._get_table()
        self.date = date

    def _get_table(self) -> Table:
        return Table(class_name="contenu_temoin", is_from_div=True, html=self._html)

    def model(self) -> Witness:
        return Witness(
            id=self.id,
            doc_id=self.doc_id,
            work_id=self.work_id,
            date=self.date,
            foliation=self.foliation,
            status=self.status,
            siglum=self.siglum,
        )

    @property
    def id(self) -> str:
        matches = self._html.xpath("div[@class='temoin']")
        for m in matches:
            return m.get("id")

    @property
    def work_id(self) -> str:
        matches = self._html.xpath("div[@class='temoin']/a[contains(@href, 'oeuvre')]")
        for m in matches:
            path = m.get("href")
            return parse_id(url=path)

    @property
    def foliation(self) -> str | None:
        matches = self._html.xpath("div[@class='temoin']/div[@class='reperage']/div")
        return matches[0].text.strip()

    @property
    def siglum(self) -> str | None:
        return self._details.find_key("Sigle", class_name="dettem")

    @property
    def status(self) -> str | None:
        return self._details.find_key("Etat du témoin", class_name="dettem")
