from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich.text import Text

from src.dbconnection import Database


def show_task(outfile: str) -> None:
    console = Console()
    task = Panel(
        Text(f"to file: '{outfile}'", justify="center", style="italic"),
        title="Writing results",
        padding=1,
    )
    console.print(task)


def dump_works(database: str) -> dict:
    console = Console()
    with Progress(SpinnerColumn(), TimeElapsedColumn(), console=console) as p:
        _ = p.add_task("")
        output = {"works": {}}
        results = output["works"]
        db = Database(persistent_file=database, restart=False)
        for w in db.works.iter_rows():
            query = f"""
    SELECT wit.* FROM Witness wit
    WHERE wit.work_url LIKE '{w["url"]}'
    """
            wit_rel = db.conn.sql(query=query)
            witnesses = [
                {k: v for k, v in zip(wit_rel.columns, w)} for w in wit_rel.fetchall()
            ]

            query = f"""
    SELECT el.* FROM ExternalLinks el
    JOIN WorkReferences wr ON el.link = wr.external_link
    WHERE wr.work_url LIKE '{w["url"]}'
    """
            ref_rel = db.conn.sql(query=query)
            external_links = [
                {k: v for k, v in zip(ref_rel.columns, el)} for el in ref_rel.fetchall()
            ]
            results.update(
                {
                    w["url"]: {
                        "metadata": w,
                        "witnesses": witnesses,
                        "external_links": external_links,
                    }
                }
            )
    return output


def dump_manuscripts(database: str) -> dict:
    console = Console()
    with Progress(SpinnerColumn(), TimeElapsedColumn(), console=console) as p:
        _ = p.add_task("")
        output = {"manuscripts": {}}
        results = output["manuscripts"]
        db = Database(persistent_file=database, restart=False)
        for m in db.documents.iter_rows():
            # Skip imprimés
            if "manuscrit" not in m["url"]:
                continue
            query = f"""
    SELECT w.* FROM Witness w 
    WHERE w.document_url LIKE '{m["url"]}'
    """
            wit_rel = db.conn.sql(query=query)
            witnesses = [
                {k: v for k, v in zip(wit_rel.columns, w)} for w in wit_rel.fetchall()
            ]
            query = f"""
    SELECT el.* FROM ExternalLinks el
    JOIN DocumentReferences dr ON el.link = dr.external_link
    WHERE dr.document_url LIKE '{m["url"]}'
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

    return output
