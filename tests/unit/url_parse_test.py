import unittest

from jonas.models.manuscript import Manuscript
from jonas.models.work import Work
from jonas.utils import parse_url


def test_1():
    url = "http://jonas.irht.cnrs.fr/oeuvre/13710"
    id, type = parse_url(url)
    assert id == "13710"
    assert type == Work


def test_2():
    url = "https://jonas.irht.cnrs.fr/consulter/oeuvre/detail_oeuvre.php?oeuvre=27906"
    id, type = parse_url(url)
    assert id == "27906"
    assert type == Work


def test_3():
    url = "https://jonas.irht.cnrs.fr/consulter/manuscrit/detail_manuscrit.php?projet=72036"
    id, type = parse_url(url)
    assert id == "72036"
    assert type == Manuscript


if __name__ == "__main__":
    unittest.main()
