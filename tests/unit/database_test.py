import unittest
from pathlib import Path
from typing import List

from pydantic import BaseModel

from jonas.database.connection import Database


class MockTable(BaseModel):
    id: str
    names: List[str | None]
    real: bool
    nickname: str | None


class DatabaseTest(unittest.TestCase):
    persistent_path = Path(__file__).parent.joinpath("test.db")

    def test_persistent_connection(self):
        Database(self.persistent_path)
        self.assertTrue(self.persistent_path.is_file())

    def test_create_statement(self):
        actual = Database.write_create_statement(
            table_name="MockTable", model=MockTable
        )
        expected = """CREATE TABLE \
MockTable (id STRING primary key, names STRING[], real BOOLEAN, nickname STRING)\
"""
        self.assertEqual(actual, expected)

    def test_insert_duplicate_data(self):
        conn = Database(tables=[("MockTable", MockTable)])
        data = MockTable(**{"id": "123", "names": [], "real": True, "nickname": None})
        conn.insert_model(table_name="MockTable", data=data)
        actual = conn._conn.sql("SELECT real FROM MockTable").fetchone()[0]
        self.assertTrue(actual)

        # Update the record
        data = MockTable(**{"id": "123", "names": [], "real": False, "nickname": None})
        conn.insert_model(table_name="MockTable", data=data)
        actual = conn._conn.sql("SELECT real FROM MockTable").fetchone()[0]
        self.assertFalse(actual)

    def test_insert_duplicate_null_data(self):
        conn = Database(tables=[("MockTable", MockTable)])
        data = MockTable(
            **{"id": "123", "names": [], "real": True, "nickname": "Jerry"}
        )
        conn.insert_model(table_name="MockTable", data=data)
        actual = conn._conn.sql("SELECT real FROM MockTable").fetchone()[0]

        # Update the record
        data = MockTable(**{"id": "123", "names": [], "real": False, "nickname": None})
        conn.insert_model(table_name="MockTable", data=data)
        actual = conn._conn.sql("SELECT nickname FROM MockTable").fetchone()[0]
        self.assertEqual(actual, "Jerry")

    def tearDown(self):
        if self.persistent_path.is_file():
            self.persistent_path.unlink()


if __name__ == "__main__":
    unittest.main()
