from fastapi import FastAPI

from .db import get_cursor

app = FastAPI()


@app.get("/invoices/{invoice_no}")
def read_invoice(invoice_no: str):
    cur = get_cursor()
    cur.execute(f"SELECT * FROM invoices WHERE number = '{invoice_no}'")
    return cur.fetchone()
