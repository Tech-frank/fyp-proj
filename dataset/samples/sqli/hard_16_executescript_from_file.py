import sqlite3
from pathlib import Path


def apply_schema(db_path, schema_file="schema.sql"):
    conn = sqlite3.connect(db_path)
    conn.executescript(Path(schema_file).read_text(encoding="utf-8"))
    conn.close()
