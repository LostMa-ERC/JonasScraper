from jonas.models.manuscript import Manuscript
from jonas.models.work import Work
from jonas.parse_csv import parse_csv
from jonas.utils import parse_url

from .base import WorkFlowManager


class NewUrls(WorkFlowManager):

    def __init__(self, database_path=":memory:"):
        super().__init__(database_path)

    def scrape(self, infile: str, column: str) -> None:
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
