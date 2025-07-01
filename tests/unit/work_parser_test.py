from jonas.parsers.work import WorkScraper, iterate_witnesses_from_work
from jonas.pool import Requester

URL = "https://jonas.irht.cnrs.fr/oeuvre/13710"
ID = "13710"


def test_work_metadata(progress_bar):
    html = Requester(progress_bar=progress_bar).retrieve_html(url=URL)
    work = WorkScraper(url=URL, html=html)
    m = work.validate()
    assert m.id == ID


def test_work_witnesses(progress_bar):
    html = Requester(progress_bar=progress_bar).retrieve_html(url=URL)
    work = WorkScraper(url=URL, html=html)
    for wit in iterate_witnesses_from_work(work_id=work.id, work_html=html):
        assert wit.work_id == ID
        if wit.foliation:
            assert wit.foliation.startswith("Folio")
