from pathlib import Path

import duckdb

from src.datamodels import ExternalLink, Manuscript, Witness


def parse_connection_file(fp: str | Path) -> duckdb.DuckDBPyConnection:
    if isinstance(fp, Path):
        fp = str(fp)
    return duckdb.connect(fp)


class Table:
    def __init__(self, conn: duckdb.DuckDBPyConnection, table_name: str, pk: str):
        self.conn = conn
        self.name = table_name
        self.columns = conn.table(table_name).columns
        self.update_columns = [c for c in self.columns if c != pk]
        self.pk = pk
        self.update_statement = ", ".join(
            [f"{c} = EXCLUDED.{c}" for c in self.update_columns]
        )

    def iter_rows(self):
        keys = self.columns
        for m in self.all.fetchall():
            yield {k: v for k, v in zip(keys, m)}

    @property
    def all(self) -> duckdb.DuckDBPyRelation:
        return self.conn.table(self.name).select("*")

    def has_key(self, key: str) -> bool:
        rel = self.conn.table(self.name).filter(f"{self.pk} like '{key}'")
        rows, _ = rel.shape
        if rows > 0:
            return True
        else:
            return False

    def insert(self, row: dict, do_nothing: bool = False) -> None:
        v_string = ", ".join(["?" for _ in row.values()])
        c_string = ", ".join(row.keys())
        if not do_nothing:
            query = f"""
    INSERT INTO {self.name} ({c_string})
    VALUES ({v_string})
    ON CONFLICT DO UPDATE 
    SET {self.update_statement}
            """
        else:
            query = f"""
    INSERT INTO {self.name} ({c_string})
    VALUES ({v_string})
    ON CONFLICT DO NOTHING
            """
        self.conn.execute(query=query, parameters=list(row.values()))


class Database:
    def __init__(self, persistent_file: str | Path, restart: bool) -> None:
        self.conn = parse_connection_file(fp=persistent_file)
        self.witnesses = self.create_table(
            table_name="Witness",
            columns=[n for n in Witness.__annotations__],
            pk="href, manuscript_url",
            drop=restart,
        )
        self.manuscripts = self.create_table(
            table_name="Manuscript",
            columns=[n for n in Manuscript.__annotations__],
            pk="url",
            drop=restart,
        )
        self.links = self.create_table(
            table_name="ExternalLinks",
            columns=[n for n in ExternalLink.__annotations__],
            pk="link",
            drop=restart,
        )

        self.manuscript_references = self.create_table(
            table_name="ManuscriptReferences",
            columns=["manuscript_url", "external_link"],
            pk="manuscript_url, external_link",
            drop=restart,
        )

    def create_table(
        self, table_name: str, columns: list, drop: bool, pk: str
    ) -> Table:
        if drop:
            query = f"DROP TABLE IF EXISTS {table_name}"
            self.conn.execute(query)
        c_list = ", ".join([f"{c} TEXT" for c in columns])
        c_list += f", PRIMARY KEY ({pk})"
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({c_list})"
        self.conn.execute(query)
        return Table(conn=self.conn, table_name=table_name, pk=pk)
