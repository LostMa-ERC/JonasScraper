from collections import Counter
from datetime import datetime
from pathlib import Path

from rich.console import Console

from jonas.database.connection import Database
from jonas.pool import Requester
from jonas.progress import ProgressBar, Spinner, show_table_counts
from jonas.scrape import scrape_html


class WorkFlowManager:

    chunk_size = 25
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

    def show_title(self):
        self.console.clear()
        self.console.rule(f"Results saved in database: '{self.db_path}'")
        show_table_counts(conn=self.conn, console=self.console)

    def scrape_urls(self, chunks: list[list], insert_wits: bool = True) -> None:
        total = Counter(x for xs in chunks for x in set(xs)).total()
        completed = 0
        self.show_title()
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
                self.show_title()

    def write_output(self, outdir: Path):
        outdir = Path(outdir)
        with Spinner(console=self.console, task="Writing output"):
            query = r"""
        SELECT
            wt.id,
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
                f"\nView a list of witnesses in this CSV file: '{outfile.absolute()}'"
            )
