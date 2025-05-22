import unittest

from src.scrapers.utils import parse_id
from src.pool import Requester
from src.scrapers.work import WorkScraper, iterate_witnesses_from_work


class TestWorkParsing(unittest.TestCase):
    def setUp(self):
        self.url = "https://jonas.irht.cnrs.fr/oeuvre/13710"
        self.work_id = "13710"
        self.html = Requester.retrieve_html(url=self.url)

    def test_work_metadata(self):
        """The parsed HTML should be validated and have the expected ID."""
        work = WorkScraper(url=self.url, html=self.html)
        m = work.validate()
        self.assertEqual(m.id, self.work_id)

    def test_work_witnesses(self):
        """The parsed HTML should have valid witnesses."""
        id = parse_id(url=self.url)
        self.assertEqual(id, self.work_id)
        for wit in iterate_witnesses_from_work(work_id=id, work_html=self.html):
            self.assertEqual(wit.work_id, self.work_id)
            self.assertGreaterEqual(len(wit.doc_id), 4)
            if wit.foliation:
                assert wit.foliation.startswith("Folio")
            print(wit)


if __name__ == "__main__":
    unittest.main()
