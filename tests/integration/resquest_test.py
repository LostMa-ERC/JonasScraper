import pytest

from jonas.database.connection import Database
from jonas.parsers.work import WorkScraper
from jonas.pool import Requester

URLS = pytest.urls


def test_works(progress_bar):
    db = Database()
    for url, html in Requester(progress_bar=progress_bar).pool_requests(urls=URLS):
        work = WorkScraper(url=url, html=html)
        model = work.validate()
        db.insert_model(table_name="Work", data=model)
        assert model.language == "oil-français"

    table_count = db.table("Work").count("*").fetchone()[0]
    assert table_count == len(URLS)
