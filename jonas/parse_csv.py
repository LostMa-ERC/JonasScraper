import casanova

from jonas.models.manuscript import Manuscript
from jonas.models.work import Work
from jonas.utils import parse_url


def parse_csv(infile: str, column_name: str) -> set:
    urls = []
    with open(infile, "r") as f:
        reader = casanova.reader(f)
        for url in reader.cells(column_name):
            id, url_type = parse_url(url)
            if url_type == Work:
                url_type = "Work"
                canonic_url = f"http://jonas.irht.cnrs.fr/oeuvre/{id}"
            elif url_type == Manuscript:
                url_type = "Manuscript"
                canonic_url = f"http://jonas.irht.cnrs.fr/manuscrit/{id}"
            else:
                url_type = None
                canonic_url = None
            if canonic_url:
                urls.append(canonic_url)
    return set(urls)
