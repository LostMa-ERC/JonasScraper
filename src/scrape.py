import requests
from lxml import html
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.text import Text

from src.dbconnection import Database
from src.manuscrit import ManuscriptPage, Document, Witness
from src.oeuvre import WorkPage, Work


class Scraper:

    WORK_BASE = "jonas.irht.cnrs.fr/oeuvre/"
    MANUSCRIPT_BASE = "jonas.irht.cnrs.fr/manuscrit/"

    def __init__(
        self,
        urls: list,
        redo: bool = False,
        restart: bool = False,
        database: str | None = None,
    ):
        self.urls = urls
        self.urls_to_process = []
        # Set up database
        self.db = Database(persistent_file=database, restart=restart)
        # Save whether to redo URLs already in database
        self.redo = redo
        # Set up console / screen
        self.console = Console()
        self.show_task()

    def request(self, url: str) -> html.Element:
        try:
            response = requests.get(url)
        except Exception as e:
            if isinstance(e, requests.exceptions.ConnectionError):
                return
            else:
                raise e
        byte_data = response.content
        source_code = html.fromstring(byte_data)
        return source_code

    def show_task(self):
        self.console.clear()

        n_urls = len(self.urls)

        if n_urls == 1:
            text = f"URL: '{self.urls[0]}'"
        elif n_urls > 1:
            unfinished = len(self.urls_to_process)
            finished = len(self.urls) - unfinished
            text = f"{finished} Finished | {unfinished} Unfinished"
        else:
            self.console.print(f"No Jonas URLs detected.")
            exit()

        task = Panel(
            Text(text, justify="center", style="italic"),
            title="Scraping Jonas",
            padding=1,
        )
        self.console.print(task)

    def scrape_manuscript(
        self, url: str, html: html.Element
    ) -> list[Witness, Document]:
        db = self.db
        # Scrape the page
        page = ManuscriptPage(html=html, url=url)
        # Into the database's manuscript table, insert the manuscript data
        db.documents.insert(page.manuscript.__dict__)
        # Into the database's witness table, insert each witness
        for wit in page.witnesses:
            db.witnesses.insert(wit.__dict__)
        # For each external reference on the manuscript page,
        for ref in page.links:
            # Relate the link to the manuscript in the relational table
            manuscript_ref_relation = {"document_url": url, "external_link": ref.link}
            db.document_references.insert(manuscript_ref_relation, do_nothing=True)
            # Insert the link in the links table
            db.links.insert(ref.__dict__)
        return page.witnesses + [page.manuscript]

    def scrape_work(self, url: str, html: html.Element) -> list[Witness, Work]:
        db = self.db
        # Scrape the page
        page = WorkPage(html=html, url=url)
        # Into the database's works table, insert the work data
        if page.work:
            db.works.insert(page.work.__dict__)
            # Into the database's witnesses table, insert the work's witnesses
            for wit in page.witnesses:
                db.witnesses.insert(wit.__dict__)
        return page.witnesses + [page.work]

    def get_missing_urls(self) -> list:
        if self.redo:
            return sorted(self.urls)
        else:
            urls = []
            for url in self.urls:
                if self.MANUSCRIPT_BASE in url:
                    if not self.db.documents.has_key(url):
                        urls.append(url)
                elif self.WORK_BASE in url:
                    if not self.db.works.has_key(url):
                        urls.append(url)
            return sorted(urls)

    def count_work_types(self) -> None:
        work_table = self.db.conn.table(self.db.works.name)
        n_rows, _ = work_table.shape
        if n_rows > 0:
            rel = (
                work_table.select("keyword_p0 as subject")
                .filter("subject is not null")
                .aggregate("subject, count(*) as total")
                .order("total desc, subject")
            )
            self.console.print(rel)
        witnesses_table = self.db.conn.table(self.db.witnesses.name)
        n_w_rows, _ = witnesses_table.shape
        manuscript_table = self.db.conn.table(self.db.documents.name)
        n_m_rows, _ = manuscript_table.shape
        t = f"""Witnesses: {n_w_rows}\t| Works: {n_rows}\t| Documents: {n_m_rows}
        """
        self.console.print(Text(t, justify="center"))

    def run(self):
        single_url = False
        if len(self.urls) == 1:
            single_url = True
        with Progress(
            TextColumn("{task.description}"), SpinnerColumn(), TimeElapsedColumn()
        ) as p:
            t = p.add_task("Sorting URLs")
            self.urls_to_process = self.get_missing_urls()
        with Progress(
            TextColumn("{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console,
        ) as p:
            t = p.add_task(f"Scraping", total=len(self.urls_to_process))
            for url in self.urls_to_process:
                self.show_task()
                self.count_work_types()
                self.console.print("Requesting URL ", url)
                html_tree = self.request(url=url)
                # If there was a connection error, move on
                # (have user try again later when connection is better)
                if not html_tree is not None:
                    continue
                # Scrape manuscript page
                if self.MANUSCRIPT_BASE in url:
                    result = self.scrape_manuscript(html=html_tree, url=url)
                # Scrape work page
                elif self.WORK_BASE in url:
                    result = self.scrape_work(html=html_tree, url=url)
                p.advance(task_id=t)
            self.show_task()
            self.count_work_types()
            if single_url:
                for r in result:
                    self.console.print(r)
