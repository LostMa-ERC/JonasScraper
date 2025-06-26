import importlib.metadata
from pathlib import Path

import casanova
import click
from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from src.database.connection import Connection
from src.models.manuscript import Manuscript
from src.models.witness import Witness
from src.models.work import Work
from src.parse_csv import parse_csv
from src.pool import Requester
from src.sorter import Sorter

# This name must match the package name ('name' kwarg) in the TOML file.
__identifier__ = importlib.metadata.version("jonas-scraper")


@click.group
@click.version_option(__identifier__)
def cli():
    pass


# -------------------------------
# Scrape from standard input
# -------------------------------
@cli.command("url")
@click.argument("url")
@click.option(
    "--outfile",
    required=False,
    default="jonas_witnesses.csv",
    type=click.Path(file_okay=True, dir_okay=False),
)
def scrape_url(url: str, outfile: str):
    outfile = Path(outfile)
    console = Console()
    conn = Connection()
    sorter = Sorter(conn=conn)
    with Progress(TextColumn("{task.description}"), SpinnerColumn()) as p:
        _ = p.add_task("Scraping...")
        html = Requester.retrieve_html(url=url)
    page, witnesses = sorter(url=url, html=html)

    # Print the scraped page's contents
    console.print(Panel(Pretty(page)))

    # Complement the witness data
    # Determine if the witnesses need document or work information
    get_work_detail = False
    if not isinstance(page, Work):
        get_work_detail = True
    # Store the additional witness data in an array
    wit_table = Table()
    wit_table.add_column("Witness")
    wit_fieldnames = [f"witness_{k}" for k in Witness.__annotations__.keys()]
    # Make the new URLs to scrape
    if get_work_detail:
        wits = {
            f"http://jonas.irht.cnrs.fr/oeuvre/{wit.work_id}": wit for wit in witnesses
        }
        wit_table.add_column("Work")
        model_fieldnames = [f"work_{k}" for k in Work.__annotations__.keys()]
    else:
        wits = {
            f"http://jonas.irht.cnrs.fr/manuscrit/{wit.doc_id}": wit
            for wit in witnesses
        }
        wit_table.add_column("Manuscript")
        model_fieldnames = [
            f"manuscript_{k}" for k in Manuscript.__annotations__.keys()
        ]
    with (
        Progress(
            TextColumn("{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as p,
        open(outfile, "w") as f,
    ):
        fieldnames = model_fieldnames + wit_fieldnames
        writer = casanova.writer(f, fieldnames=fieldnames)
        wit_urls = list(wits.keys())
        t = p.add_task("Fetching URLs...", total=len(wit_urls))
        for url, html in Requester.pool_requests(urls=wit_urls, timeout=10):
            page, _ = sorter(url=url, html=html)
            wit_model = wits[url]
            wit_table.add_row(Pretty(wit_model), Pretty(page))
            row = list(page.model_dump().values()) + list(
                wit_model.model_dump().values()
            )
            writer.writerow(row)
            p.advance(t)
    console.print(wit_table)
    console.print(
        f"View a list of the witnesses in this CSV file: '{outfile.absolute()}'"
    )


# -------------------------------
# Scrape from CSV
# -------------------------------
@cli.command("file")
@click.option(
    "-i",
    "--infile",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=True,
)
@click.option(
    "-o",
    "--outdir",
    type=click.Path(file_okay=False, dir_okay=True),
    required=True,
)
@click.option(
    "-c",
    "--column-name",
    type=click.STRING,
    required=True,
)
def scrape_command(infile, outdir, column_name):
    outdir = Path(outdir)
    outdir.mkdir(exist_ok=True)

    outfile = outdir.joinpath(f"{Path(infile).stem}_witnesses.csv")
    database = outdir.joinpath("jonas.db")

    conn = Connection(database_path=database)
    sorter = Sorter(conn=conn)
    console = Console()

    urls_in_csv = parse_csv(infile=infile, column_name=column_name)
    # Remove from CSV set of URLs those that have been scraped
    done_works = [row[0] for row in conn._conn.sql('select id from "Work"').fetchall()]
    done_manusripts = [
        row[0] for row in conn._conn.sql("select id from Manuscript").fetchall()
    ]
    urls = []
    for url in urls_in_csv:
        item_id, url_type = sorter.parse_url(url=url)
        # If the sorter's URL parser didn't work as expected, skip this URL
        if not item_id:
            continue
        # If the Work URL isn't in the database, add it to the list to scrape
        if url_type == Work and item_id not in done_works:
            urls.append(url)
        # If the Manuscript URL isn't in the database, add it to the list to scrape
        elif url_type == Manuscript and item_id not in done_manusripts:
            urls.append(url)

    with Progress(
        TextColumn("{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as p:
        t = p.add_task("Fetching URLs...", total=len(urls))
        for url, html in Requester.pool_requests(urls=urls, timeout=10):
            sorter(url=url, html=html)
            p.advance(t)

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
    remaining_urls = [t[0] for t in conn._conn.sql(query).fetchall()]
    total_remaining = len(remaining_urls)
    if total_remaining < 100 or click.confirm(
        f"There are {total_remaining} URLs with additional information relevant \
to the discovered witnesses. Do you want to scrape all of them?"
    ):
        with Progress(
            TextColumn("{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as p:
            t = p.add_task("Fetching discovered URLs...", total=total_remaining)
            for url, html in Requester.pool_requests(urls=remaining_urls, timeout=10):
                # Do not add to witnesses table while filling out its complementary info
                sorter(url=url, html=html, insert_wits=False)
                p.advance(t)

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
    result = conn._conn.sql(query=query)
    result.write_csv(str(outfile))

    console.print(f"view a list of witnesses in this CSV file: '{outfile.absolute()}'")


if __name__ == "__main__":
    cli()
