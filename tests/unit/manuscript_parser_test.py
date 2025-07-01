from jonas.parsers.manuscript import ManuscriptScraper
from jonas.parsers.manuscript.witness import iterate_witnesses_from_document
from jonas.pool import Requester

URL = "https://jonas.irht.cnrs.fr/manuscrit/82723"
ID = "82723"


def test_manuscript_metadata(progress_bar):
    html = Requester(progress_bar=progress_bar).retrieve_html(url=URL)
    work = ManuscriptScraper(url=URL, html=html)
    m = work.validate()
    assert m.id == ID


def test_manuscript_witnesses(progress_bar):
    html = Requester(progress_bar=progress_bar).retrieve_html(url=URL)
    for wit in iterate_witnesses_from_document(doc_id=ID, doc_html=html):
        assert wit.doc_id == ID
        if wit.foliation:
            assert wit.foliation.startswith("Folio")
