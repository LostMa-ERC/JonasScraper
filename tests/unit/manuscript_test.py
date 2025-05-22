import unittest
from src.scrapers.utils import parse_id
from src.pool import Requester
from src.scrapers.manuscript import ManuscriptScraper
from src.scrapers.manuscript.witness import iterate_witnesses_from_document


class TestDocumentParsing(unittest.TestCase):
    def setUp(self):
        self.url = "https://jonas.irht.cnrs.fr/manuscrit/82723"
        self.doc_id = "82723"
        self.html = Requester.retrieve_html(url=self.url)

    def test_work_metadata(self):
        """The parsed HTML should be validated and have the expected ID."""
        work = ManuscriptScraper(url=self.url, html=self.html)
        m = work.validate()
        self.assertEqual(m.id, self.doc_id)
        print(m)

    def test_work_witnesses(self):
        """The parsed HTML should have valid witnesses."""
        id = parse_id(url=self.url)
        self.assertEqual(id, self.doc_id)
        for wit in iterate_witnesses_from_document(doc_id=id, doc_html=self.html):
            self.assertEqual(wit.doc_id, self.doc_id)
            self.assertGreaterEqual(len(wit.doc_id), 4)
            if wit.foliation:
                assert wit.foliation.startswith("Folio")


if __name__ == "__main__":
    unittest.main()
