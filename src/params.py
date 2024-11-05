import re
from collections import namedtuple

import duckdb
import ural
from rich.prompt import Prompt

Args = namedtuple("Args", field_names=["url", "infile", "column_name"])


def get_args(url: str | None, infile: str | None, column_name: str | None) -> Args:
    if infile and not column_name:
        column_name = Prompt.ask("Column name: ")
    elif not infile and not url:
        format = Prompt.ask("Input format", choices=["url", "CSV file"])
        if format == "url":
            url = Prompt.ask("URL")
        else:
            infile = Prompt.ask("CSV file")
            column_name = Prompt.ask("URL column")
    return Args(url, infile, column_name)


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


def get_urls(url: str | None, infile: str | None, column_name: str | None) -> list:
    args = get_args(url, infile, column_name)

    if args.url:
        urls = verify_urls([args.url])
    else:
        links = [
            t[0]
            for t in duckdb.read_csv(args.infile)
            .filter(f'"{args.column_name}" IS NOT NULL')
            .aggregate(args.column_name)
            .fetchall()
        ]
        urls = verify_urls(links)

    return urls
