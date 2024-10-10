import click

from src.manuscripts import dump_manuscripts, scrape_manuscripts

from .__version__ import __identifier__


@click.group
@click.version_option(__identifier__)
def cli():
    pass


@cli.group
def scrape():
    pass


@cli.group
def dump():
    pass


@dump.command("manuscripts")
@click.option("-f", "--database", type=click.Path(exists=True), required=True)
@click.option("-o", "--outfile")
def dump_manuscript_command(database, outfile):
    dump_manuscripts(database, outfile)


@scrape.command("manuscripts")
@click.option("-i", "--infile", type=click.Path(exists=True), required=True)
@click.option("-c", "--column-name", type=click.STRING, required=True)
@click.option("-f", "--database", required=True)
@click.option("--restart", is_flag=True, show_default=True, default=False)
@click.option("--redo", is_flag=True, show_default=True, default=False)
def scrape_manuscripts_command(infile, column_name, database, restart, redo):
    scrape_manuscripts(infile, column_name, database, restart, redo)


if __name__ == "__main__":
    cli()
