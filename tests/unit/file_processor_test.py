from src.cli.file import FileProcessor

URLS = [
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


def test_list_chunking():
    fp = FileProcessor()
    fp.chunk_size = 12
    chunks = fp.chunk_urls(urls=URLS)
    for chunk in chunks:
        assert len(chunk) == 12
    assert len(chunks) == 1
