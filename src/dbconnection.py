from pathlib import Path

import duckdb

from src.datamodels import ExternalLink, Document, Witness, Work


def parse_connection_file(fp: str | Path) -> duckdb.DuckDBPyConnection:
    if isinstance(fp, Path):
        fp = str(fp)
    return duckdb.connect(fp)


class Table:
    def __init__(self, conn: duckdb.DuckDBPyConnection, table_name: str, pk: str):
        self.conn = conn
        self.name = table_name
        self.columns = conn.table(table_name).columns
        primary_keys = [k.strip() for k in pk.split(",")]
        self.update_columns = [c for c in self.columns if c not in primary_keys]
        self.pk = pk
        self.update_statement = ", ".join(
            [
                f"{c} = COALESCE(EXCLUDED.{c}, {c})"
                for c in self.update_columns
                if self.update_columns
            ]
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
        values = list(row.values())
        v_string = ", ".join(["?" for _ in values])
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
        try:
            self.conn.execute(query=query, parameters=values)
        except Exception as e:
            print(query)
            print(values)
            raise e


class Database:
    def __init__(self, persistent_file: str | Path, restart: bool) -> None:
        self.conn = parse_connection_file(fp=persistent_file)

        # Main tables
        self.witnesses = self.create_table(
            table_name="Witness",
            columns=[n for n in Witness.__annotations__],
            pk="work_url, document_url",
            drop=restart,
        )
        self.documents = self.create_table(
            table_name="Document",
            columns=[n for n in Document.__annotations__],
            pk="url",
            drop=restart,
        )
        self.links = self.create_table(
            table_name="ExternalLinks",
            columns=[n for n in ExternalLink.__annotations__],
            pk="link",
            drop=restart,
        )
        self.works = self.create_table(
            table_name="Works",
            columns=[n for n in Work.__annotations__],
            pk="url",
            drop=restart,
        )

        # Relational tables
        self.document_references = self.create_table(
            table_name="DocumentReferences",
            columns=["document_url", "external_link"],
            pk="document_url, external_link",
            drop=restart,
        )
        self.work_references = self.create_table(
            table_name="WorkReferences",
            columns=["work_url", "external_link"],
            pk="work_url, external_link",
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
