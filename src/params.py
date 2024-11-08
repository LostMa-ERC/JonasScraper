import re
from dataclasses import dataclass

import duckdb
import ural
from rich.prompt import Prompt
from rich.console import Console


@dataclass
class Params:
    database: str
    infile: str | None
    column_name: str | None
    input_url: str | None
    urls: list | None = None

    @classmethod
    def from_click_args(
        cls,
        url: str | None,
        infile: str | None,
        column_name: str | None,
        database: str | None,
    ) -> "Params":
        Console().clear()
        if infile and not column_name:
            column_name = Prompt.ask("Column name: ")
        elif not infile and not url:
            print("\n")
            format = Prompt.ask("Input format", choices=["url", "csv"])
            if format == "url":
                url = Prompt.ask("URL")
            else:
                infile = Prompt.ask("CSV file")
                column_name = Prompt.ask("URL column")
        if infile and not database:
            print("\n")
            database = Prompt.ask("Database filepath")

        if url:
            urls = verify_urls([url])
        else:
            links = [
                t[0]
                for t in duckdb.read_csv(infile)
                .filter(f'"{column_name}" IS NOT NULL')
                .aggregate(column_name)
                .fetchall()
            ]
            urls = verify_urls(links)

        return Params(
            urls=urls,
            database=database,
            infile=infile,
            column_name=column_name,
            input_url=url,
        )


def verify_urls(urls: list[str]) -> list:
    # Manuscript links
    m_prefix_permalink = "http://jonas.irht.cnrs.fr/manuscrit/{}"
    # Work links
    w_prefix_permalink = "http://jonas.irht.cnrs.fr/oeuvre/{}"
    # URLs
    url_set = set()
    for l in urls:
        l = l.strip()
        # If the link isn't a URL, do not keep it
        if not ural.is_url(l):
            continue
        # Extract the ID
        jonas_id = re.findall(r"[oeuvre/|manuscrit/|=](\d+)$", l)
        if not len(jonas_id) == 1:
            continue
        else:
            jonas_id = jonas_id[0]
        # Standardize the url
        if "manuscrit" in l:
            url_set.add(m_prefix_permalink.format(jonas_id))
        elif "oeuvre" in l:
            url_set.add(w_prefix_permalink.format(jonas_id))
    return list(url_set)
