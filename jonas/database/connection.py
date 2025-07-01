import duckdb
from pydantic import BaseModel

from jonas.models.manuscript import Manuscript
from jonas.models.witness import Witness
from jonas.models.work import Work


def get_duckdb_table_names(conn: duckdb.DuckDBPyConnection) -> list[str]:
    return [t[0] for t in conn.sql("show tables").fetchall()]


TABLES = [
    ("Work", Work),
    ("Witness", Witness),
    ("Manuscript", Manuscript),
]


class Database:
    def __init__(
        self,
        database_path: str | None = None,
        tables: list[tuple[str, BaseModel]] = TABLES,
    ) -> None:
        if database_path:
            self._conn = duckdb.connect(database=database_path)
        else:
            self._conn = duckdb.connect()
        created_tables = get_duckdb_table_names(self._conn)
        for table_name, table_model in tables:
            if table_name not in created_tables:
                stmt = self.write_create_statement(
                    table_name=table_name, model=table_model
                )
                try:
                    self._conn.execute(stmt)
                except Exception as e:
                    print(stmt)
                    raise e

    @staticmethod
    def write_create_statement(table_name: str, model: BaseModel) -> str:
        columns = []
        schema = model.model_json_schema()["properties"]
        for name, annotation in schema.items():
            if annotation.get("anyOf"):
                possible_types = annotation["anyOf"]
                dtype = [t["type"] for t in possible_types if t["type"] != "null"][0]
            else:
                dtype = annotation["type"]
            if dtype == "array":
                dtype = "string[]"
            if name.lower() == "id":
                columns.append(f"{name} {dtype.upper()} primary key")
            else:
                columns.append(f"{name} {dtype.upper()}")
        return f"CREATE TABLE {table_name} ({', '.join(columns)})"

    def insert_csv(self, table_name: str, model: BaseModel, csv_file: str):

        def compose_set_statement(col: str) -> str:
            return f"""
{col} = CASE WHEN EXCLUDED.{col} IS NULL THEN {col} ELSE EXCLUDED.{col} END
            """

        update_statement = ", ".join(
            [
                compose_set_statement(c)
                for c in model.__annotations__.keys()
                if c != "id"
            ]
        )
        stmt = f"""
INSERT INTO {table_name} SELECT * FROM read_csv('{csv_file}')
ON CONFLICT DO UPDATE SET {update_statement}
        """
        try:
            self._conn.execute(query=stmt)
        except Exception as e:
            print(stmt)
            raise e

        from rich import print

        print("\n\nEND OF INSERT")

    def insert_model(self, table_name: str, data: BaseModel):
        data_dict = data.model_dump()
        # Freeze the parameters
        parameters = data_dict.copy()
        # Create the values and conflict strings
        col_string = ", ".join([f"${c} " for c in data_dict.keys()])
        data_dict.pop("id")

        def compose_set(col: str) -> str:
            return f"""
    {col} = CASE WHEN EXCLUDED.{col} IS NULL THEN {col} ELSE EXCLUDED.{col} END
            """

        update_stmt = ", ".join([compose_set(c) for c in data_dict.keys()])
        # Compose the full insert statement
        stmt = f"""\
INSERT INTO {table_name} VALUES ({col_string}) ON CONFLICT DO UPDATE SET {update_stmt}\
"""
        try:
            self._conn.execute(query=stmt, parameters=parameters)
        except Exception as e:
            print(stmt)
            raise e

    def table(self, table_name: str) -> duckdb.DuckDBPyRelation:
        return self._conn.table(table_name).sort("id")
