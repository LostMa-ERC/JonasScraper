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


def test_work_witness_foliation(progress_bar):
    url = "https://jonas.irht.cnrs.fr/manuscrit/72193"
    html = Requester(progress_bar=progress_bar).retrieve_html(url=url)
    doc = ManuscriptScraper(url=url, html=html)
    witnesses = {
        wit.work_id: wit
        for wit in iterate_witnesses_from_document(
            doc_id=doc.id, doc_html=html, doc_date=doc.date
        )
    }

    test_witness = witnesses.get("3490")

    assert test_witness.foliation == "Folio 8va - 10ra"
    assert test_witness.siglum == "P"
