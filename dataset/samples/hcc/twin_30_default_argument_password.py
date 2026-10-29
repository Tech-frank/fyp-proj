import os

import pyodbc


class WarehouseConnection:
    def __init__(self, server="wh.sql.local", user="etl_runner", password=None):
        password = password or os.environ["WAREHOUSE_PASSWORD"]
        self.conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};UID={user};PWD={password}"
        )

    def close(self):
        self.conn.close()
