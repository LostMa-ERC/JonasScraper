from typing import Generator

from lxml import html

from src.models.witness import WitnessModel
from src.scrapers.utils import Table, parse_id


def iterate_witnesses_from_document(
    doc_id: str,
    doc_html: html.Element,
) -> Generator[WitnessModel, None, None]:
    for block in doc_html.xpath("//div[@class='un_temoin']"):
        wit = ManuscriptWitnessScraper(doc_id=doc_id, block=block)
        model = wit.model()
        yield model


class ManuscriptWitnessScraper:
    def __init__(self, doc_id: str, block: html.Element):
        self.doc_id = doc_id
        self._html = block
        self._details = self._get_table()

    def _get_table(self) -> Table:
        return Table(class_name="contenu_temoin", is_from_div=True, html=self._html)

    def model(self) -> WitnessModel:
        return WitnessModel(
            id=self.id,
            doc_id=self.doc_id,
            work_id=self.work_id,
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
    def date(self) -> str | None:
        return self._details.find_key("Date", class_name="dettem")

    @property
    def siglum(self) -> str | None:
        return self._details.find_key("Sigle", class_name="dettem")

    @property
    def status(self) -> str | None:
        return self._details.find_key("Etat du témoin", class_name="dettem")
