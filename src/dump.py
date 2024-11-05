import json

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TimeElapsedColumn,
)
from rich.text import Text

from src.dbconnection import Database


def dump_manuscripts(database: str, outfile: str):
    console = Console()
    task = Panel(
        Text(f"to file: '{outfile}'", justify="center", style="italic"),
        title="Writing results",
        padding=1,
    )
    console.print(task)
    with Progress(SpinnerColumn(), TimeElapsedColumn(), console=console) as p:
        _ = p.add_task(task)
        output = {"manuscripts": {}}
        results = output["manuscripts"]
        db = Database(persistent_file=database, restart=False)
        for m in db.manuscripts.iter_rows():
            query = f"""
    SELECT w.* FROM Witness w 
    WHERE w.manuscript_url LIKE '{m["url"]}'
    """
            wit_rel = db.conn.sql(query=query)
            witnesses = [
                {k: v for k, v in zip(wit_rel.columns, w)} for w in wit_rel.fetchall()
            ]
            query = f"""
    SELECT el.* FROM ExternalLinks el
    JOIN ManuscriptReferences mr ON el.link = mr.external_link
    WHERE mr.manuscript_url LIKE '{m["url"]}'
    """
            ref_rel = db.conn.sql(query=query)
            external_links = [
                {k: v for k, v in zip(ref_rel.columns, el)} for el in ref_rel.fetchall()
            ]
            results.update(
                {
                    m["url"]: {
                        "metadata": m,
                        "witnesses": witnesses,
                        "external_links": external_links,
                    }
                }
            )

        with open(outfile, mode="w", encoding="utf-8") as of:
            json.dump(obj=output, fp=of, indent=4, ensure_ascii=False)


# def scrape_manuscripts(scraper: BatchScraper | URLScraper):
#     if isinstance(scraper, BatchScraper):
#         console = scraper.console
#         expected_length = scraper.expected_length
#         urls = scraper.jonas_urls
#         db = scraper.db
#         redo = scraper.redo

#         with Progress(
#             TextColumn("{task.description}"),
#             BarColumn(),
#             MofNCompleteColumn(),
#             TimeElapsedColumn(),
#             console=console,
#         ) as p:
#             scraped_jonas_urls = Counter()
#             skipped_jonas_urls = Counter()
#             skipped_other_urls = Counter()
#             t1 = p.add_task(f"Scraping", total=expected_length)
#             for jonas_url in urls:
#                 # If the URL isn't of a Jonas manuscript, skip
#                 if not ural.is_url(jonas_url) and not jonas_url.startswith(
#                     "http://jonas.irht.cnrs.fr/manuscrit/"
#                 ):
#                     skipped_other_urls.update([jonas_url])
#                     continue

#                 # If the Jonas manuscript page's data is already in the database, skip
#                 if not redo and db.manuscripts.has_key(jonas_url):
#                     skipped_jonas_urls.update([jonas_url])
#                     p.advance(t1)
#                     continue

#                 # Scrape the manuscript page
#                 page = JonasPage(url=jonas_url)
#                 scraped_jonas_urls.update([jonas_url])

#                 # Insert the manuscript's data
#                 manuscript = page.manuscript
#                 db.manuscripts.insert(manuscript.__dict__)

#                 # Insert the witnesses' data
#                 for wit in page.witnesses:
#                     db.witnesses.insert(wit.__dict__, do_nothing=True)

#                 # Insert the external links' data
#                 for ref in page.links:
#                     man_ref_rel = {
#                         "manuscript_url": jonas_url,
#                         "external_link": ref.link,
#                     }
#                     db.manuscript_references.insert(man_ref_rel, do_nothing=True)
#                     db.links.insert(ref.__dict__)

#                 p.advance(t1)

#         table1 = Table(title="Scraping Results")
#         table1.add_column(
#             f"Unique values in '{scraper.column_name}'",
#             justify="right",
#             style="cyan",
#             no_wrap=True,
#         )
#         table1.add_column(str(len(urls)), justify="right", style="red")
#         table1.add_row("Jonas URLs (scraped)", str(scraped_jonas_urls.total()))
#         table1.add_row("Jonas URLs (found in DB)", str(skipped_jonas_urls.total()))
#         table1.add_row("Other URLs (not scraped)", str(skipped_other_urls.total()))

#         n_manuscripts = db.manuscripts.all.shape[0]
#         n_witnesses = db.witnesses.all.shape[0]
#         table2 = Table(title="Database Contents")
#         table2.add_column("Table", justify="right", style="cyan", no_wrap=True)
#         table2.add_column("Rows", justify="right", style="red")
#         table2.add_row("Manuscript", str(n_manuscripts))
#         table2.add_row("Witness", str(n_witnesses))

#         console.print(table1)
#         console.print(table2)
#         console.print(f"DuckDB database file: {scraper.database_path}\n")
