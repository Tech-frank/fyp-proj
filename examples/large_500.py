# --- from hard_01_constant_table_concat.py
TABLE = "user_accounts"


def count_accounts(cursor):
    cursor.execute("SELECT COUNT(*) FROM " + TABLE)
    return cursor.fetchone()[0]

# --- from hard_02_placeholder_list_format.py
def products_by_ids(cursor, ids):
    query = "SELECT sku, name FROM products WHERE id IN ({})".format(",".join("?" * len(ids)))
    cursor.execute(query, ids)
    return cursor.fetchall()

# --- from hard_03_whitelisted_order_by.py
SORTABLE = {"newest": "created_at DESC", "oldest": "created_at ASC", "title": "title ASC"}


def list_articles(cursor, sort="newest"):
    order = SORTABLE.get(sort, SORTABLE["newest"])
    cursor.execute(f"SELECT id, title FROM articles ORDER BY {order}")
    return cursor.fetchall()

# --- from hard_04_logged_fstring_query.py
import logging

log = logging.getLogger(__name__)


def fetch_user(cursor, user_id):
    log.debug(f"SELECT * FROM users WHERE id = {user_id}")
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    return cursor.fetchone()

# --- from hard_05_select_word_in_message.py
def menu_prompt(options):
    choices = ", ".join(options)
    return f"Please select an option from: {choices}"

# --- from hard_06_percent_s_with_params.py
def find_order(cursor, ref):
    cursor.execute("SELECT * FROM orders WHERE ref = %s", (ref,))
    return cursor.fetchone()

# --- from hard_07_schema_from_constant_list.py
TABLES = ["users", "orders", "payments"]


def truncate_all(conn):
    cur = conn.cursor()
    for table in TABLES:
        cur.execute(f"TRUNCATE TABLE {table} CASCADE")
    conn.commit()

# --- from hard_08_migration_constant_format.py
COLUMN = "last_login"
DEFAULT = "NULL"


def add_column(cursor):
    sql = "ALTER TABLE users ADD COLUMN {} TIMESTAMP DEFAULT {}".format(COLUMN, DEFAULT)
    cursor.execute(sql)

# --- from hard_09_named_params_dict.py
def update_email(cursor, user_id, email):
    cursor.execute(
        "UPDATE users SET email = %(email)s WHERE id = %(id)s",
        {"email": email, "id": user_id},
    )

# --- from hard_10_sqlalchemy_text_bound.py
from sqlalchemy import text

ACTIVE_FILTER = "status = 'active'"


def active_members(conn, club_id):
    stmt = text("SELECT name FROM members WHERE club_id = :club AND " + ACTIVE_FILTER)
    return conn.execute(stmt, {"club": club_id}).fetchall()

# --- from hard_11_error_message_with_query_words.py
class QueryError(Exception):
    pass


def require_rows(rows, table):
    if not rows:
        raise QueryError(f"No rows returned from {table}; check the WHERE clause.")
    return rows

# --- from hard_12_print_sql_for_debugging.py
def run(cursor, statement, params=()):
    print("Executing: " + statement)
    cursor.execute(statement, params)
    return cursor.fetchall()

# --- from hard_13_orm_filter.py
from shop.models import Customer


def customers_named(name):
    return list(Customer.objects.filter(last_name__iexact=name).values("id", "email"))

# --- from hard_14_sqlalchemy_core_select.py
from sqlalchemy import select

from .tables import accounts


def account_by_number(conn, number):
    stmt = select(accounts).where(accounts.c.number == number)
    return conn.execute(stmt).first()

# --- from hard_15_static_query_concat_lines.py
def monthly_summary(cursor):
    cursor.execute(
        "SELECT date_trunc('month', created_at) AS month, COUNT(*) "
        + "FROM signups "
        + "GROUP BY 1 ORDER BY 1"
    )
    return cursor.fetchall()

# --- from hard_16_executescript_from_file.py
import sqlite3
from pathlib import Path


def apply_schema(db_path, schema_file="schema.sql"):
    conn = sqlite3.connect(db_path)
    conn.executescript(Path(schema_file).read_text(encoding="utf-8"))
    conn.close()

# --- from hard_17_int_cast_not_used_in_sql.py
def page_number(raw):
    try:
        return max(1, int(raw))
    except ValueError:
        return 1


def fetch_page(cursor, raw_page, size=20):
    page = page_number(raw_page)
    cursor.execute("SELECT id FROM items ORDER BY id LIMIT ? OFFSET ?", (size, (page - 1) * size))
    return cursor.fetchall()

# --- from hard_18_column_list_from_constants.py
EXPORT_COLUMNS = ("id", "email", "created_at")


def export_users(cursor):
    columns = ", ".join(EXPORT_COLUMNS)
    cursor.execute("SELECT " + columns + " FROM users")
    return cursor.fetchall()

# --- from hard_19_sql_template_comment.py
# Example of a vulnerable query, kept here for documentation only:
#   cursor.execute("SELECT * FROM users WHERE name = '" + name + "'")


def find_by_name(cursor, name):
    cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
    return cursor.fetchall()

# --- from hard_20_fstring_in_html_not_sql.py
def render_result(username, count):
    return f"<p>Selected {count} rows where owner is {username}</p>"

# --- from hard_21_mysql_identifier_quoted_constant.py
REPORT_VIEW = "v_daily_revenue"


def refresh_report(cursor):
    cursor.execute("REFRESH MATERIALIZED VIEW %s" % REPORT_VIEW)

# --- from hard_22_query_builder_whitelist_fields.py
FILTERABLE = ("status", "priority")


def find_tasks(cursor, filters):
    clauses, params = [], []
    for field in FILTERABLE:
        if field in filters:
            clauses.append(f"{field} = ?")
            params.append(filters[field])
    where = " AND ".join(clauses) or "1=1"
    cursor.execute("SELECT id, title FROM tasks WHERE " + where, params)
    return cursor.fetchall()

# --- from hard_23_executemany_static.py
def insert_readings(cursor, readings):
    cursor.executemany("INSERT INTO readings (sensor, value) VALUES (?, ?)", readings)

# --- from hard_24_format_for_filename.py
def export_path(table_name, day):
    return "exports/{}_{}.csv".format(table_name, day.isoformat())

# --- from hard_25_savepoint_name_constant.py
SAVEPOINT = "before_import"


def import_batch(cursor, rows):
    cursor.execute(f"SAVEPOINT {SAVEPOINT}")
    try:
        cursor.executemany("INSERT INTO staging (a, b) VALUES (?, ?)", rows)
    except Exception:
        cursor.execute(f"ROLLBACK TO SAVEPOINT {SAVEPOINT}")
        raise

# --- from hard_26_psycopg2_sql_module.py
from psycopg2 import sql


def count_in(cursor, table):
    query = sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table))
    cursor.execute(query)
    return cursor.fetchone()[0]

# --- from hard_27_assert_message_query.py
def check_migration(cursor):
    cursor.execute("SELECT COUNT(*) FROM schema_version")
    version = cursor.fetchone()[0]
    assert version >= 12, f"expected schema >= 12, SELECT returned {version}"

# --- from hard_28_date_range_params.py
import datetime


def events_last_week(cursor):
    end = datetime.date.today()
    start = end - datetime.timedelta(days=7)
    cursor.execute("SELECT name, day FROM events WHERE day BETWEEN ? AND ?", (start, end))
    return cursor.fetchall()

# --- from hard_29_table_prefix_setting.py
TABLE_PREFIX = "app_"


def table(name):
    return TABLE_PREFIX + name


def drop_temp_tables(cursor):
    for name in ("tmp_import", "tmp_export"):
        cursor.execute("DROP TABLE IF EXISTS " + table(name))

# --- from hard_30_connection_string_no_query.py
import sqlite3


def open_db(name):
    path = f"data/{name}.sqlite3"
    return sqlite3.connect(path)

# --- from plain_01_fibonacci.py
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

# --- from plain_02_slugify.py
import re


def slugify(title):
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower())
    return slug.strip("-")

# --- from plain_03_http_status_check.py
import requests


def is_up(url):
    try:
        return requests.head(url, timeout=3).status_code < 400
    except requests.RequestException:
        return False

# --- from plain_04_matrix_transpose.py
def transpose(matrix):
    return [list(row) for row in zip(*matrix)]

# --- from plain_05_file_hash.py
import hashlib


def sha256_of(path, chunk=65536):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            digest.update(block)
    return digest.hexdigest()

# --- from plain_06_queue_worker.py
import queue
import threading

jobs = queue.Queue()


def worker():
    while True:
        job = jobs.get()
        try:
            job()
        finally:
            jobs.task_done()


threading.Thread(target=worker, daemon=True).start()

# --- from plain_07_markdown_heading.py
def heading(text, level=1):
    return f"{'#' * level} {text}"

# --- from plain_08_price_with_tax.py
from decimal import Decimal, ROUND_HALF_UP

VAT = Decimal("0.075")


def gross(net):
    return (Decimal(net) * (1 + VAT)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

# --- from plain_09_yaml_reader.py
import yaml


def read_pipeline(path):
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh).get("stages", [])

# --- from plain_10_chunk_list.py
def chunks(items, size):
    for start in range(0, len(items), size):
        yield items[start:start + size]

# --- from pos_01_flask_sqlite_concat.py
import sqlite3

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/users")
def get_user():
    user_id = request.args.get("id", "")
    conn = sqlite3.connect("app.db")
    row = conn.execute("SELECT id, name, email FROM users WHERE id = " + user_id).fetchone()
    conn.close()
    return jsonify(row)

# --- from pos_02_psycopg2_fstring_login.py
def check_login(cursor, username, password_hash):
    cursor.execute(
        f"SELECT id FROM accounts WHERE username = '{username}' AND pw_hash = '{password_hash}'"
    )
    return cursor.fetchone() is not None

# --- from pos_03_pymysql_percent_format.py
def orders_for_customer(conn, customer_email):
    with conn.cursor() as cur:
        cur.execute("SELECT id, total FROM orders WHERE email = '%s'" % customer_email)
        return cur.fetchall()

# --- from pos_04_format_method_delete.py
def delete_comment(db, comment_id, author):
    cur = db.cursor()
    cur.execute("DELETE FROM comments WHERE id = {} AND author = '{}'".format(comment_id, author))
    db.commit()
    return cur.rowcount

# --- from pos_05_query_variable_fstring.py
def search_products(cursor, term):
    query = f"SELECT sku, name, price FROM products WHERE name LIKE '%{term}%'"
    cursor.execute(query)
    return cursor.fetchall()

# --- from pos_06_query_built_with_augassign.py
def filter_tickets(cursor, status, assignee):
    sql = "SELECT id, title FROM tickets WHERE 1=1"
    if status:
        sql += " AND status = '" + status + "'"
    if assignee:
        sql += " AND assignee = '" + assignee + "'"
    cursor.execute(sql)
    return cursor.fetchall()

# --- from pos_07_order_by_user_column.py
def list_employees(cursor, sort_by):
    cursor.execute(f"SELECT id, name, salary FROM employees ORDER BY {sort_by}")
    return cursor.fetchall()

# --- from pos_08_table_name_from_user.py
import sqlite3


def count_rows(db_path, table):
    conn = sqlite3.connect(db_path)
    total = conn.execute("SELECT COUNT(*) FROM " + table).fetchone()[0]
    conn.close()
    return total

# --- from pos_09_sqlalchemy_text_fstring.py
from sqlalchemy import text


def recent_logins(engine, username):
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT at FROM logins WHERE username = '{username}' ORDER BY at DESC"))
        return [row.at for row in result]

# --- from pos_10_helper_builds_query.py
def build_lookup(field, value):
    return "SELECT * FROM customers WHERE " + field + " = '" + value + "'"


def lookup_customer(cursor, field, value):
    cursor.execute(build_lookup(field, value))
    return cursor.fetchone()

# --- from pos_11_django_raw_query.py
from shop.models import Product


def products_in_category(category_slug):
    return list(Product.objects.raw(
        f"SELECT * FROM shop_product WHERE category_slug = '{category_slug}'"
    ))

# --- from pos_12_django_cursor_execute.py
from django.db import connection


def mark_shipped(order_ref):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE orders SET status = 'shipped' WHERE ref = '%s'" % order_ref)

# --- from pos_13_pandas_read_sql.py
import pandas as pd


def sales_for_region(engine, region):
    return pd.read_sql(f"SELECT month, revenue FROM sales WHERE region = '{region}'", engine)

# --- from pos_14_executemany_format.py
def bulk_tag(cursor, tag, ids):
    cursor.executemany("INSERT INTO item_tags (item_id, tag) VALUES (?, '{}')".format(tag),
                       [(i,) for i in ids])

# --- from pos_15_executescript_concat.py
import sqlite3


def reset_user_data(db_path, username):
    conn = sqlite3.connect(db_path)
    conn.executescript(
        "DELETE FROM sessions WHERE user = '" + username + "';"
        "DELETE FROM carts WHERE user = '" + username + "';"
    )
    conn.close()

# --- from pos_16_fastapi_path_param.py
from fastapi import FastAPI

from .db import get_cursor

app = FastAPI()


@app.get("/invoices/{invoice_no}")
def read_invoice(invoice_no: str):
    cur = get_cursor()
    cur.execute(f"SELECT * FROM invoices WHERE number = '{invoice_no}'")
    return cur.fetchone()

# --- from pos_17_repository_class_method.py
class UserRepository:
    def __init__(self, conn):
        self.conn = conn

    def find_by_email(self, email):
        cur = self.conn.cursor()
        cur.execute("SELECT id, name FROM users WHERE email = '" + email + "'")
        return cur.fetchone()

# --- from pos_18_cli_input_search.py
import sqlite3


def main():
    name = input("Book title to search: ")
    conn = sqlite3.connect("library.db")
    cur = conn.cursor()
    cur.execute("SELECT title, author FROM books WHERE title = '%s'" % name)
    for title, author in cur.fetchall():
        print(f"{title} by {author}")


if __name__ == "__main__":
    main()

