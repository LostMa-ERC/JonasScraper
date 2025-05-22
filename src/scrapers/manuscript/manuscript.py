from lxml import html

from src.models.manuscript import ManuscriptModel
from src.scrapers.utils import Table, parse_id, clean


class ManuscriptScraper:
    def __init__(self, url: str, html: html.Element):
        self._url = url
        self.id = parse_id(url)
        self._html = html
        self.identification_table = self._get_identification_table(html=html)
        self.description_table = self._get_description_table(html=html)

    def validate(self) -> ManuscriptModel:
        return ManuscriptModel.model_validate(
            {
                "id": self.id,
                "exemplar": self.exemplar,
                "date": self.date,
                "language": self.language,
            }
        )

    @classmethod
    def _get_identification_table(cls, html: html.Element) -> Table | None:
        tables = html.xpath("//div[@id='identification']//table")
        for t in tables:
            return Table(table=t)

    @classmethod
    def _get_description_table(cls, html: html.Element) -> Table | None:
        tables = html.xpath("//div[@id='description']//table")
        for t in tables:
            return Table(table=t)

    @property
    def exemplar(self) -> str | None:
        span = self.identification_table.table.xpath(
            "tr[@class='principal']/td[@class='principal']/\
                div[starts-with(@title, 'Exemplaire')]/span"
        )
        return clean(span[0].text)

    @property
    def date(self) -> str | None:
        return self.identification_table.find_key("Datation détaillée")

    @property
    def language(self) -> str | None:
        return self.identification_table.find_key("Langue principale")
