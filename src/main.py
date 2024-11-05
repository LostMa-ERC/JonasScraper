import click

from src.dump import dump_manuscripts
from src.params import get_urls
from src.scrape import Scraper

from .__version__ import __identifier__


@click.group
@click.version_option(__identifier__)
def cli():
    pass


# -------------------------------
# Scraping Command
# -------------------------------
@cli.command("scrape")
@click.option("-u", "--url", type=click.STRING)
@click.option(
    "-i",
    "--infile",
    type=click.Path(exists=True),
)
@click.option(
    "-c",
    "--column-name",
    type=click.STRING,
)
@click.option(
    "-d",
    "--database",
    type=click.STRING,
    default=":memory:",
)
@click.option("--restart", is_flag=True, show_default=True, default=False)
@click.option("--redo", is_flag=True, show_default=True, default=False)
def scrape_command(url, infile, column_name, database, restart, redo):
    urls = get_urls(url=url, infile=infile, column_name=column_name)
    scraper = Scraper(
        urls=urls,
        database=database,
        restart=restart,
        redo=redo,
    )
    scraper.run()


# -------------------------------


@cli.group
def dump():
    pass


@dump.command("manuscripts")
@click.option("-f", "--database", type=click.Path(exists=True), required=True)
@click.option("-o", "--outfile")
def dump_manuscript_command(database, outfile):
    dump_manuscripts(database, outfile)


if __name__ == "__main__":
    cli()
