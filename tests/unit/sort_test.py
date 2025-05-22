import unittest

from src.sorter import Sorter
from src.models.work import WorkModel


class SortTest(unittest.TestCase):
    def test_1(self):
        url = "http://jonas.irht.cnrs.fr/oeuvre/13710"
        id, t = Sorter.parse_url(url)
        self.assertEqual(id, "13710")
        self.assertEqual(t, WorkModel)

    def test_2(self):
        url = (
            "https://jonas.irht.cnrs.fr/consulter/oeuvre/detail_oeuvre.php?oeuvre=27906"
        )
        id, t = Sorter.parse_url(url)
        self.assertEqual(id, "27906")
        self.assertEqual(t, WorkModel)

    def test_3(self):
        url = "https://jonas.irht.cnrs.fr/consulter/manuscrit/detail_manuscrit.php?projet=72036"
        id, t = Sorter.parse_url(url)
        self.assertEqual(id, "72036")
        self.assertNotEqual(t, WorkModel)


if __name__ == "__main__":
    unittest.main()
