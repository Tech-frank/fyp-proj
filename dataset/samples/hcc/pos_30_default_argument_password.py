import pyodbc


class WarehouseConnection:
    def __init__(self, server="wh.sql.local", user="etl_runner", password="Etl#Runner2021!"):
        self.conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};UID={user};PWD={password}"
        )

    def close(self):
        self.conn.close()
