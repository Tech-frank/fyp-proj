from flask import Flask, request

from .db import connect

app = Flask(__name__)


@app.post("/login")
def login():
    user = request.form["username"]
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT pw_hash FROM users WHERE username = '" + user + "'")
    row = cur.fetchone()
    return ("ok", 200) if row else ("unknown user", 401)
