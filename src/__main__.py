import importlib.metadata

import click
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    SpinnerColumn,
)
from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty
from pathlib import Path

from src.database.connection import Connection, TABLES
from src.parse_csv import parse_csv
from src.pool import Requester
from src.sorter import Sorter
from src.models.work import Work

# This name must match the package name ('name' kwarg) in the TOML file.
__identifier__ = importlib.metadata.version("jonas-scraper")


@click.group
@click.version_option(__identifier__)
def cli():
    pass


@cli.command("url")
@click.argument("url")
def scrape_url(url: str):
    console = Console()
    conn = Connection()
    sorter = Sorter(conn=conn)
    with Progress(TextColumn("{task.description}"), SpinnerColumn()) as p:
        _ = p.add_task("Scraping...")
        html = Requester.retrieve_html(url=url)
    page, witnesses = sorter(url=url, html=html)
    # Print the page
    console.print(Panel(Pretty(page)))
    # Print the witnesses
    console.rule("Witnesses")
    for wit in witnesses:
        console.print(Pretty(wit))


# -------------------------------
# Scrape from CSV
# -------------------------------
@cli.command("scrape")
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

    outfile = outdir.joinpath(f"{Path(infile).stem}.csv")
    database = outdir.joinpath("jonas.db")

    urls = parse_csv(infile=infile, column_name=column_name, outfile=outfile)
    conn = Connection(database_path=database)
    sorter = Sorter(conn=conn)
    console = Console()
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

    for table_name, _ in TABLES:
        console.rule(table_name)
        print(conn.table(table_name).describe())
        fp = outdir.joinpath(f"{table_name}.csv")
        conn.table(table_name).write_csv(str(fp))


if __name__ == "__main__":
    cli()
