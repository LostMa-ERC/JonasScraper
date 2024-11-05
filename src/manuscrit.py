import re

from lxml import html

from src.datamodels import ExternalLink, Manuscript, Witness


class ManuscriptPage:
    def __init__(self, url: str, html: html.Element) -> None:
        self.url = url
        self.html = html
        self.witnesses = self.list_temoins(jonas_url=url)
        self.manuscript = self.get_manuscript_details()
        self.links = self.get_links()

    def clean_text(self, text: str) -> str:
        s = re.sub(pattern=r"\s{2,}", repl=" ", string=text)
        return s.strip()

    def list_xpath(self, xpath: str) -> list[html.HtmlElement, None]:
        matches = []
        for match in self.html.xpath(xpath):
            if match is not None:
                matches.append(match)
        return matches

    def get_text(self, root: html.HtmlElement, path: str) -> html.HtmlElement | None:
        tag = root.xpath(path)
        if len(tag) > 0 and tag[0] is not None:
            text_content = tag[0].text
            return self.clean_text(text_content)

    @staticmethod
    def clean_work_url(path: str) -> str:
        id = path.split("=")[-1]
        return f"http://jonas.irht.cnrs.fr/oeuvre/{id}"

    @staticmethod
    def complete_url_path(path: str) -> str:
        return "https://jonas.irht.cnrs.fr/" + path.removeprefix("../../")

    def list_temoins(self, jonas_url: str) -> list[Witness]:
        witness_xpath = '//div[@class="un_temoin"]'
        pages_path = './/div[@class="reperage"]/div[1]'
        work_path = ".//a[@href]"
        witnesses = self.list_xpath(xpath=witness_xpath)
        results = []
        for witness in witnesses:
            relative_path = witness.xpath(work_path)[0].get("href")
            work = self.clean_work_url(relative_path)
            pages = witness.xpath(pages_path)
            if pages is not None:
                page_text = self.clean_text(pages[0].text)
                results.append(
                    Witness(
                        work_url=work,
                        pages=page_text,
                        manuscript_url=jonas_url,
                        siglum=None,
                    )
                )
            else:
                results.append(
                    Witness(
                        work_url=work, pages=None, manuscript_url=jonas_url, siglum=None
                    )
                )
        return results

    def get_links(self) -> list[ExternalLink]:
        links_xpath = '//a[@class="lienExterne"]'
        links = []
        for link in self.list_xpath(links_xpath):
            links.append(ExternalLink(link=link.get("href"), source=link.text))
        return links

    def get_manuscript_details(self) -> Manuscript:
        identification_table_path = '//div[@id="identification"]/div[@class="bloccontenu"]/table[1]//tr[@class="principal"]'
        exemplar = None
        date = None
        language_principal = None
        for row in self.list_xpath(identification_table_path):
            title = row.xpath('td[@class="elttitre"]')[0].text
            if title == "Exemplaire":
                data = self.get_text(root=row, path='td[@class="principal"]/div/span')
                exemplar = data
            else:
                data = self.get_text(root=row, path='td[@class="normal"]')
                if "Datation" in title:
                    date = data
                elif "Langue" in title:
                    language_principal = data

        return Manuscript(
            url=self.url,
            exemplar=exemplar,
            date=date,
            language_principal=language_principal,
        )
