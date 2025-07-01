import pytest

from jonas.manager.base import WorkFlowManager

URLS = pytest.urls


def test_list_chunking():
    fp = WorkFlowManager()
    fp.chunk_size = 12
    chunks = fp.chunk_urls(urls=URLS)
    for chunk in chunks:
        assert len(chunk) == 12
    assert len(chunks) == 1
