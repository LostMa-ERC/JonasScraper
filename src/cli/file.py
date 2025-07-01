from collections import Counter
from datetime import datetime
from pathlib import Path

from rich.console import Console

from src.database.connection import Database
from src.models.manuscript import Manuscript
from src.models.work import Work
from src.parse_csv import parse_csv
from src.pool import Requester
from src.progress import ProgressBar, Spinner
from src.scrape import scrape_html
from src.utils import parse_url


class FileProcessor:
    chunk_size = 21
    completed = 0

    def __init__(self, database_path: str = ":memory:") -> None:
        # Paths
        self.db_path = database_path
        # Console
        self.console = Console()
        # Database
        self.db = Database(database_path=self.db_path)
        self.conn = self.db._conn

    def chunk_urls(self, urls: list[str]) -> list[list]:
        return [
            urls[i : i + self.chunk_size] for i in range(0, len(urls), self.chunk_size)
        ]

    def scrape_infile_urls(self, infile: str, column: str) -> None:
        urls_in_csv = parse_csv(infile=infile, column_name=column)
        done_works = [
            row[0] for row in self.conn.sql('select id from "Work"').fetchall()
        ]
        done_manusripts = [
            row[0] for row in self.conn.sql("select id from Manuscript").fetchall()
        ]
        urls = []
        for url in urls_in_csv:
            item_id, url_type = parse_url(url=url)
            # If the Scraper's URL parser didn't work as expected, skip this URL
            if not item_id:
                continue
            # If the Work URL isn't in the database, add it to the list to scrape
            if url_type == Work and item_id not in done_works:
                urls.append(url)
            # If the Manuscript URL isn't in the database, add it to the list to scrape
            elif url_type == Manuscript and item_id not in done_manusripts:
                urls.append(url)
        sorted_urls = sorted(urls)
        chunks = self.chunk_urls(sorted_urls)
        self.scrape_urls(chunks=chunks)

    def scrape_urls(self, chunks: list[list], insert_wits: bool = True) -> None:
        total = Counter(x for xs in chunks for x in set(xs)).total()
        completed = 0
        with ProgressBar(console=self.console) as p:
            request = Requester(progress_bar=p, throttle=True)
            t = p.add_task(
                "Total URLs",
                total=total,
                completed=completed,
                progress_type="green",
            )
            for batch in chunks:
                batch_results = []
                for url, html in request.pool_requests(urls=batch):
                    page_results = scrape_html(
                        url=url,
                        html=html,
                        insert_wits=insert_wits,
                    )
                    batch_results.append(page_results)
                    completed += 1
                    p.update(t, completed=completed)

                for page in batch_results:
                    if page.work:
                        self.db.insert_model(table_name="Work", data=page.work)
                    elif page.manuscript:
                        self.db.insert_model(
                            table_name="Manuscript", data=page.manuscript
                        )
                    for witness in page.witnesses:
                        self.db.insert_model(table_name="Witness", data=witness)
                self.console.clear()
                self.console.print(self.conn.table("Witness"))

        # Confirm that everything was
        assert total == completed

    def get_supplementary_urls(self) -> list[str]:
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
        return [t[0] for t in self.conn.sql(query).fetchall()]

    def scrape_supplemental_urls(self):
        urls = self.get_supplementary_urls()
        chunks = self.chunk_urls(urls=urls)
        self.scrape_urls(chunks=chunks)

    def write_output(self, outdir: Path):
        outdir = Path(outdir)
        with Spinner(console=self.console, task="Writing output"):
            query = r"""
        SELECT
            concat('http://jonas.irht.cnrs.fr/oeuvre/', wt.work_id) as work_url,
            concat('http://jonas.irht.cnrs.fr/manuscrit/', wt.doc_id) as ms_url,
            columns(wk.*) as "work_\0",
            columns(wt.*) as "witness_\0",
            columns(ma.*) as "manuscript_\0"
        FROM Witness wt
        LEFT JOIN Work wk ON wt.work_id = wk.id
        LEFT JOIN Manuscript ma ON wt.doc_id = ma.id
        ORDER BY work_url
        """
            result = self.conn.sql(query=query)

            # Write outfile
            timestamp = datetime.now().timestamp()
            outfile = outdir.joinpath(f"witnesses_{timestamp}.csv")
            result.write_csv(str(outfile))

            self.console.print(
                f"view a list of witnesses in this CSV file: '{outfile.absolute()}'"
            )
