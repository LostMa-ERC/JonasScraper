import casanova

from src.models.manuscript import Manuscript
from src.models.work import Work
from src.sorter import Sorter


def parse_csv(infile: str, column_name: str, outfile: str) -> set:
    urls = []
    with open(infile, "r") as f, open(outfile, "w") as of:
        enricher = casanova.enricher(f, of, add=["table_id", "table_name"])
        for row, url in enricher.cells(column_name, with_rows=True):
            id, url_type = Sorter.parse_url(url)
            if url_type == Work:
                url_type = "Work"
                canonic_url = f"http://jonas.irht.cnrs.fr/oeuvre/{id}"
            elif url_type == Manuscript:
                url_type = "Manuscript"
                canonic_url = f"http://jonas.irht.cnrs.fr/manuscrit/{id}"
            else:
                url_type = None
                canonic_url = None
            enricher.writerow(row, (id, url_type))
            if canonic_url:
                urls.append(canonic_url)
    return set(urls)
