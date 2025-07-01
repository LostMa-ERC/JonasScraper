from collections import namedtuple

import lxml.html
from jonas.models.manuscript import Manuscript
from jonas.models.work import Work
from jonas.parsers.manuscript import (
    ManuscriptScraper,
    iterate_witnesses_from_document,
)
from jonas.parsers.work import WorkScraper, iterate_witnesses_from_work
from jonas.utils import parse_url

PageResults = namedtuple("PageResults", field_names=["work", "witnesses", "manuscript"])


def scrape_html(
    url: str,
    html: lxml.html.Element,
    insert_wits: bool = True,
) -> PageResults:
    results = {"work": None, "witnesses": [], "manuscript": None}
    id, type = parse_url(url=url)
    if type == Work:
        content = WorkScraper(url=url, html=html)
        results.update({"work": content.validate()})
    elif type == Manuscript:
        content = ManuscriptScraper(url=url, html=html)
        results.update({"manuscript": content.validate()})
    if insert_wits:
        if type == Manuscript:
            wits = [
                wit
                for wit in iterate_witnesses_from_document(
                    doc_id=id, doc_html=html, doc_date=content.date
                )
            ]
        else:
            wits = [
                wit for wit in iterate_witnesses_from_work(work_id=id, work_html=html)
            ]
        results.update({"witnesses": wits})
    return PageResults(**results)
