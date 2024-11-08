import click

from src.dump import dump_manuscripts, show_task, dump_works
from src.params import Params
from src.scrape import Scraper
import json

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
)
@click.option("--restart", is_flag=True, show_default=True, default=False)
@click.option("--redo", is_flag=True, show_default=True, default=False)
def scrape_command(url, infile, column_name, database, restart, redo):
    params = Params.from_click_args(
        url=url, infile=infile, column_name=column_name, database=database
    )
    scraper = Scraper(
        urls=params.urls,
        database=params.database,
        restart=restart,
        redo=redo,
    )
    scraper.run()


# -------------------------------


@cli.group
def dump():
    pass


@dump.command("works")
@click.option("-f", "--database", type=click.Path(exists=True), required=True)
@click.option("-o", "--outfile", required=True)
def dump_work_command(database, outfile):
    show_task(outfile=outfile)
    output = dump_works(database)
    with open(outfile, mode="w", encoding="utf-8") as of:
        json.dump(obj=output, fp=of, indent=4, ensure_ascii=False)


@dump.command("manuscripts")
@click.option("-f", "--database", type=click.Path(exists=True), required=True)
@click.option("-o", "--outfile", required=True)
def dump_manuscript_command(database, outfile):
    show_task(outfile=outfile)
    output = dump_manuscripts(database)
    with open(outfile, mode="w", encoding="utf-8") as of:
        json.dump(obj=output, fp=of, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    cli()
