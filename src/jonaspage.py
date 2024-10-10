import re

import requests
from lxml import html

from src.datamodels import ExternalLink, Manuscript, Witness


class JonasPage:
    def __init__(self, url: str) -> None:
        self.url = url
        self.html = self.request_page(url)
        self.witnesses = self.list_temoins(jonas_url=url)
        self.manuscript = self.get_manuscript_details()
        self.links = self.get_links()

    def request_page(self, url: str) -> html.HtmlElement:
        response = requests.get(url)
        byte_data = response.content
        source_code = html.fromstring(byte_data)
        return source_code

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
    def complete_url_path(path: str) -> str:
        return "https://jonas.irht.cnrs.fr/" + path.removeprefix("../../")

    def list_temoins(self, jonas_url: str) -> list[Witness]:
        witness_xpath = '//div[@class="un_temoin"]'
        author_path = './/span[@class="auteur"]'
        title_path = './/span[@class="titre"]'
        pages_path = './/div[@class="reperage"]/div[1]'
        work_path = ".//a[@href]"
        witnesses = self.list_xpath(xpath=witness_xpath)
        results = []
        for witness in witnesses:
            author = self.get_text(root=witness, path=author_path)
            title = self.get_text(root=witness, path=title_path)
            relative_path = witness.xpath(work_path)[0].get("href")
            work = self.complete_url_path(relative_path)
            pages = witness.xpath(pages_path)
            if pages is not None:
                page_text = self.clean_text(pages[0].text)
                results.append(
                    Witness(
                        href=work,
                        author=author,
                        title=title,
                        pages=page_text,
                        manuscript_url=jonas_url,
                    )
                )
            else:
                results.append(
                    Witness(
                        href=work,
                        author=author,
                        title=title,
                        pages=None,
                        manuscript_url=jonas_url,
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
