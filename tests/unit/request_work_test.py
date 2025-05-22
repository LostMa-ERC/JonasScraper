import unittest

from src.pool import Requester
from collections import Counter
from lxml import html as lxml_html

URLS = [
    "http://jonas.irht.cnrs.fr/oeuvre/13710",
    "http://jonas.irht.cnrs.fr/oeuvre/5641",
    "http://jonas.irht.cnrs.fr/oeuvre/9187",
    "http://jonas.irht.cnrs.fr/oeuvre/13250",
]


class TestWorkRequest(unittest.TestCase):
    def test_pooling(self):
        """Should return all URLs' parsed HTML pages."""
        counter = Counter()
        expected = len(URLS)
        for url, html in Requester.pool_requests(URLS, max_workers=1):
            counter.update([url])
            self.assertIsInstance(html, lxml_html.HtmlElement)
        self.assertEqual(counter.total(), expected)

    def test_request(self):
        """Should return a valid work page's parsed HTML"""
        html = Requester.retrieve_html(url=URLS[0])
        data_tables = html.xpath("//table")
        counter = Counter(data_tables)
        self.assertGreaterEqual(counter.total(), 2)


if __name__ == "__main__":
    unittest.main()
