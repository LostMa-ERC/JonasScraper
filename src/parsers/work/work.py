from lxml import html

from src.models.work import Work
from src.parsers.utils import Table, clean
from src.utils import parse_id


class WorkScraper:
    def __init__(self, url: str, html: html.Element):
        self._url = url
        self.id = parse_id(url)
        self._html = html
        self.identification_table = self._get_identification_table(html=html)
        self.description_table = self._get_description_table(html=html)

    def validate(self) -> Work:
        return Work.model_validate(
            {
                "id": self.id,
                "title": self.title,
                "author": self.author,
                "incipit": self.incipit,
                "form": self.form,
                "date": self.date,
                "language": self.language,
                "n_verses": self.n_verses,
                "meter": self.meter,
                "rhyme_scheme": self.rhyme_scheme,
                "scripta": self.scripta,
                "keywords": self.keywords,
            }
        )

    @classmethod
    def _get_identification_table(cls, html: html.Element) -> Table | None:
        table = Table(html=html, class_name="table_identification")
        if table.table is not None:
            return table

    @classmethod
    def _get_description_table(cls, html: html.Element) -> Table | None:
        table = Table(html=html, class_name="descripteurs")
        if table.table is not None:
            return table

    @property
    def title(self) -> str | None:
        return self.identification_table.find_class("titre")

    @property
    def author(self) -> str | None:
        return self.identification_table.find_class("auteur")

    @property
    def incipit(self) -> str | None:
        return self.identification_table.find_class("incipit")

    @property
    def form(self) -> str | None:
        return self.identification_table.find_key("Forme")

    @property
    def date(self) -> str | None:
        return self.identification_table.find_key("Datation détaillée")

    @property
    def language(self) -> str | None:
        return self.identification_table.find_key("Langue principale")

    @property
    def n_verses(self) -> str | None:
        return self.description_table.find_key(
            key="Nombre de vers", class_name="ed_descripteur"
        )

    @property
    def meter(self) -> str | None:
        return self.description_table.find_key(
            key="Type de vers", class_name="ed_descripteur"
        )

    @property
    def rhyme_scheme(self) -> str | None:
        return self.description_table.find_key(
            key="Schéma de rimes", class_name="ed_descripteur"
        )

    @property
    def scripta(self) -> str | None:
        return self.description_table.find_key(
            key="Langue auteur", class_name="ed_descripteur"
        )

    @property
    def keywords(self) -> list:
        keywords = []
        matches = self._html.xpath("//ul[@class='thesaurus']")
        if len(matches) == 1:
            thesaurus = matches[0]
            motclef_P0 = thesaurus.xpath("li[@class='motclef_P0']")
            if len(motclef_P0) == 1:
                keyword_p0 = clean(motclef_P0[0].text)
                keywords.append(keyword_p0)
            motclef_P1 = thesaurus.xpath("li[@class='motclef_P1']")
            if len(motclef_P1) == 1:
                keyword_p1 = clean(motclef_P0[0].text)
                keywords.append(keyword_p1)
            motclef_P0 = thesaurus.xpath("li[@class='motclef_E2']")
            if len(motclef_P0) == 1:
                keyword_e2 = clean(motclef_P0[0].text)
                keywords.append(keyword_e2)
        return keywords

    @property
    def links(self) -> list:
        tags = self.html.xpath("//a[@class='lienExterne']")
        links = []
        for t in tags:
            link = t.get("href")
            links.append(link)
        return links
