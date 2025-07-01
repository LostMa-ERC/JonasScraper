from .base import WorkFlowManager


class SupplementalURLs(WorkFlowManager):

    def __init__(self, database_path=":memory:"):
        super().__init__(database_path)

    def scrape(self) -> list[str]:
        query = """
SELECT url, count(*) FROM (
SELECT
    concat('http://jonas.irht.cnrs.fr/manuscrit/', wt.doc_id) url
FROM Witness wt
LEFT JOIN Manuscript ms ON ms.id = wt.doc_id
WHERE ms.id IS NULL
UNION
SELECT
    concat('http://jonas.irht.cnrs.fr/oeuvre/', wt.work_id) url
FROM Witness wt
LEFT JOIN Work wk ON wk.id = wt.work_id
WHERE wk.id IS NULL
) GROUP BY url
"""
        urls = [t[0] for t in self.conn.sql(query).fetchall()]
        chunks = self.chunk_urls(urls=urls)
        self.scrape_urls(chunks=chunks, insert_wits=False)
