import pytest

from jonas.progress import ProgressBar


def pytest_configure():
    pytest.urls = [
        "http://jonas.irht.cnrs.fr/oeuvre/10000",
        "http://jonas.irht.cnrs.fr/oeuvre/10001",
        "http://jonas.irht.cnrs.fr/oeuvre/10002",
        "http://jonas.irht.cnrs.fr/oeuvre/10003",
        "http://jonas.irht.cnrs.fr/oeuvre/10004",
        "http://jonas.irht.cnrs.fr/oeuvre/10005",
        "http://jonas.irht.cnrs.fr/oeuvre/10006",
        "http://jonas.irht.cnrs.fr/oeuvre/10007",
        "http://jonas.irht.cnrs.fr/oeuvre/10008",
        "http://jonas.irht.cnrs.fr/oeuvre/10009",
        "http://jonas.irht.cnrs.fr/oeuvre/10010",
        "http://jonas.irht.cnrs.fr/oeuvre/10011",
    ]


@pytest.fixture
def progress_bar():
    with ProgressBar() as y:
        yield y
