from lxml import html


def clean(t: str | None) -> str:
    if t:
        t = t.strip()
        t = t.replace("\n", " ")
        t = t.replace("\t", " ")
        t = t.replace("  ", " ")
        return t


class HtmlTable:
    def __init__(
        self,
        root: html.Element,
        table_class: str,
        idx: int = 0,
        is_from_div: bool = False,
    ) -> None:
        if is_from_div:
            tables = root.xpath(f"div[@class='{table_class}']//table")
        else:
            tables = root.xpath(f"//table[@class='{table_class}']")
        if len(tables) > 0:
            self.table = tables[idx]
        else:
            self.table = None

    def find_td(self, label: str, td_class: str = "elttitre") -> str | None:
        xpath = f"tr/td[@class='{td_class}' and contains(text(), '{label}')]/following-sibling::td"
        matches = self.table.xpath(xpath)
        if len(matches) > 0:
            t = matches[0].text
            if t:
                return clean(t)

    def td_by_class(self, td_class: str) -> str:
        xpath = f"tr/td[@class='{td_class}']"
        matches = self.table.xpath(xpath)
        if len(matches) > 0:
            t = matches[0].text
            if t:
                return clean(t)
