import importlib.metadata
from pathlib import Path

import click

from src.manager.new_urls import NewUrls
from src.manager.supplement import SupplementalURLs

# This name must match the package name ('name' kwarg) in the TOML file.
__identifier__ = importlib.metadata.version("jonas-scraper")


@click.group()
@click.version_option(__identifier__)
def cli():
    pass


# -------------------------------
# Scrape from CSV
# -------------------------------
@cli.command("new-urls")
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
def scrape_new_urls(infile, outdir, column_name):
    # Compose a path to the database in the output directory
    db_path = Path(outdir).joinpath("jonas.db")

    # Create an instance of the File Processor class
    fp = NewUrls(database_path=db_path)

    # Run the steps of processing a CSV file
    fp.scrape(infile=infile, column=column_name)
    fp.write_output(outdir=outdir)


@cli.command("supplement")
@click.option(
    "-d",
    "--database-path",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=False,
)
@click.option(
    "-o",
    "--outdir",
    type=click.Path(file_okay=False, dir_okay=True),
    required=True,
)
def supplement_existing_urls(database_path, outdir):
    # Compose a path to the database in the output directory
    if not database_path:
        database_path = Path(outdir).joinpath("jonas.db")

    # Create an instance of the File Processor class
    fp = SupplementalURLs(database_path=database_path)

    # Run the steps of supplementing a database's existing data
    fp.scrape()
    fp.write_output(outdir=outdir)


if __name__ == "__main__":
    cli()
