from typing import Generator

from lxml import html

from jonas.models.witness import Witness
from jonas.parsers.utils import Table
from jonas.utils import parse_id


def iterate_witnesses_from_work(
    work_id: str,
    work_html: html.Element,
) -> Generator[Witness | None, None, None]:
    for block in work_html.xpath("//div[@class='un_temoin temoin']"):
        wit = WorkWitnessScraper(work_id=work_id, block=block)
        try:
            model = wit.model()
        except Exception:
            continue
        yield model


class WorkWitnessScraper:
    id = None

    def __init__(self, work_id: str, block: html.Element):
        self.work_id = work_id
        self._html = block
        self._top_table = self._get_header_table()
        self._details = self._get_content_table()

    def _get_header_table(self) -> html.Element:
        for wit in self._html.xpath("table[starts-with(@id, 'temoin')]"):
            self.id = wit.get("id")
            return wit

    def _get_content_table(self) -> Table | None:
        content_tables = self._html.xpath("div[@class='contenu_temoin']/table")
        if len(content_tables) == 1:
            return Table(table=content_tables[0])

    def model(self) -> Witness:
        return Witness(
            id=self.id,
            doc_id=self.doc_id,
            work_id=self.work_id,
            date=self.date,
            siglum=self.siglum,
            status=self.status,
            foliation=self.pages,
        )

    @property
    def doc_id(self) -> str:
        matches = self._top_table.xpath("tr/th/a[starts-with(@title, 'Voir ce')]")
        href = matches[0].get("href")
        return parse_id(href)

    @property
    def date(self) -> str | None:
        return self._details.find_key("Datation", class_name="dettem")

    @property
    def siglum(self) -> str | None:
        return self._details.find_key("Sigle", class_name="dettem")

    @property
    def status(self) -> str | None:
        return self._details.find_key("Etat du témoin", class_name="dettem")

    @property
    def pages(self) -> str | None:
        return self._details.find_class(class_name="reperage")
