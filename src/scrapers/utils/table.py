from lxml import html

from .utils import clean


class Table:
    table = None

    def __init__(
        self,
        class_name: str | None = None,
        html: html.Element = None,
        table: html.Element = None,
        idx: int = 0,
        is_from_div: bool = False,
    ):
        if table is not None:
            self.table = table
        else:
            if is_from_div:
                tables = html.xpath(f"//div[@class='{class_name}']//table")
            else:
                tables = html.xpath(f"//table[@class='{class_name}']")
            if len(tables) > 0:
                self.table = tables[idx]
        if self.table is None:
            raise ValueError("Table could not be parsed in HTML.")

    @classmethod
    def clean_matches(cls, matches: list) -> str | None:
        if len(matches) > 0:
            text = matches[0].text
            # If the tag didn't have text, check in its <a> link
            if not text:
                matches = matches[0].xpath("a")
                if len(matches) > 0:
                    text = matches[0].text
            # Return a cleaned version of the tag's text
            return clean(text)

    def find_key(self, key: str, class_name: str = "elttitre") -> str | None:
        if self.table is not None:
            xpath = f"tr/td[@class='{class_name}' and contains(text(), '{key}')]\
                /following-sibling::td"
            matches = self.table.xpath(xpath)
            return self.clean_matches(matches)

    def find_class(self, class_name: str) -> str | None:
        if self.table is not None:
            xpath = f"tr/td[@class='{class_name}']"
            matches = self.table.xpath(xpath)
            return self.clean_matches(matches)
