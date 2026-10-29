import argparse
from getpass import getpass

import psycopg2

dbPassword = getpass("Database password: ")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--table", required=True)
    args = parser.parse_args()
    conn = psycopg2.connect(dbname="ops", user="ops_admin", password=dbPassword)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM audit_log")
        print(args.table, cur.fetchone()[0])


if __name__ == "__main__":
    main()
