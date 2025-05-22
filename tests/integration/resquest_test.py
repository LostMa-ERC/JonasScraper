import unittest

from src.database.connection import Connection
from src.pool import Requester
from src.scrapers.work import WorkScraper

WORK_URLS = [
    "http://jonas.irht.cnrs.fr/oeuvre/13710",
    "http://jonas.irht.cnrs.fr/oeuvre/5641",
    "http://jonas.irht.cnrs.fr/oeuvre/9187",
    "http://jonas.irht.cnrs.fr/oeuvre/13250",
]


class RequestTest(unittest.TestCase):
    def test_work(self):
        conn = Connection()
        for url, html in Requester.pool_requests(urls=WORK_URLS):
            work = WorkScraper(url=url, html=html)
            model = work.validate()
            conn.insert_model(table_name="Work", data=model)

        print(conn._conn.table("Work"))


if __name__ == "__main__":
    unittest.main()
