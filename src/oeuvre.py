from lxml import html

from src.datamodels import ExternalLink, Witness, Work
from src.utils import HtmlTable, clean


class WorkPage:
    def __init__(self, url: str, html: html.Element) -> None:
        self.url = url
        self.html = html
        self.work = self.get_work()
        self.witnesses = self.list_temoins()
        self.links = self.get_links()

    def get_work(self) -> Work:
        # Identification table for the Work
        id_table = HtmlTable(root=self.html, table_class="table_identification")
        if not id_table.table is not None:
            return
        title = id_table.find_td("Titre")
        author = id_table.find_td("Auteur")
        incipit = id_table.find_td("Incipit")
        form = id_table.find_td("Forme")
        date = id_table.find_td("Datation détaillée")
        language = id_table.find_td("Langue principale")

        # Descripteurs table for the Work
        desc_table = HtmlTable(root=self.html, table_class="descripteurs")
        n_verses = desc_table.find_td("Nombre de vers", td_class="ed_descripteur")
        meter = desc_table.find_td("Type de vers", td_class="ed_descripteur")
        rhyme_scheme = desc_table.find_td("Schéma de rimes", td_class="ed_descripteur")
        scripta = desc_table.find_td("Langue auteur", td_class="ed_descripteur")

        # Thesaurus list for the Work
        thesaurus_list = self.html.xpath("//ul[@class='thesaurus']")
        keyword_p0, keyword_p1, keyword_e2 = None, None, None
        if len(thesaurus_list) == 1:
            thesaurus = thesaurus_list[0]
            motclef_P0 = thesaurus.xpath("li[@class='motclef_P0']")
            if len(motclef_P0) == 1:
                keyword_p0 = clean(motclef_P0[0].text)
            motclef_P1 = thesaurus.xpath("li[@class='motclef_P1']")
            if len(motclef_P1) == 1:
                keyword_p1 = clean(motclef_P0[0].text)
            motclef_P0 = thesaurus.xpath("li[@class='motclef_E2']")
            if len(motclef_P0) == 1:
                keyword_e2 = clean(motclef_P0[0].text)

        # Return the Work data
        return Work(
            url=self.url,
            title=title,
            author=author,
            incipit=incipit,
            form=form,
            date=date,
            language=language,
            n_verses=n_verses,
            meter=meter,
            rhyme_scheme=rhyme_scheme,
            scripta=scripta,
            keyword_p0=keyword_p0,
            keyword_p1=keyword_p1,
            keyword_e2=keyword_e2,
        )

    @staticmethod
    def complete_url_path(path: str) -> str:
        return "https://jonas.irht.cnrs.fr/" + path.removeprefix("../../")

    @staticmethod
    def clean_manuscript_url(path: str) -> str:
        id = path.split("=")[-1]
        return f"http://jonas.irht.cnrs.fr/manuscrit/{id}"

    @staticmethod
    def clean_imprime_url(path: str) -> str:
        id = path.split("=")[-1]
        return f"http://jonas.irht.cnrs.fr/imprime/{id}"

    def list_temoins(self) -> list[Witness]:
        witnesses = self.html.xpath("//div[@class='un_temoin temoin']")

        wit_list = []

        for wit in witnesses:
            document_url = None
            # Get the Manuscript's URL from the witness's first table
            manuscript = wit.xpath("table/tr/th/a[@title='Voir ce manuscrit']")
            if len(manuscript) == 1:
                document_url = self.clean_manuscript_url(manuscript[0].get("href"))
            else:
                imprime = wit.xpath("table/tr/th/a[@title='Voir cet imprimé']")
                if len(imprime) == 1:
                    document_url = self.clean_imprime_url(imprime[0].get("href"))
            # Get the nested tables contianing the witness's information
            contents = HtmlTable(
                root=wit, table_class="contenu_temoin", is_from_div=True
            )
            pages = contents.td_by_class(td_class="reperage")
            siglum = contents.find_td(label="Sigle", td_class="dettem")

            if document_url:
                w = Witness(
                    work_url=self.url,
                    document_url=document_url,
                    pages=pages,
                    siglum=siglum,
                )
                wit_list.append(w)

        return wit_list

    def get_links(self) -> list[ExternalLink]:
        tags = self.html.xpath("//a[@class='lienExterne']")
        links = []
        for t in tags:
            link = ExternalLink(link=t.get("href"), source=t.text)
            links.append(link)
        return links


if __name__ == "__main__":
    wp = WorkPage(url="http://jonas.irht.cnrs.fr/oeuvre/1704")
    from pprint import pprint

    pprint(wp.work)
    pprint(wp.witnesses)
    pprint(wp.links)
