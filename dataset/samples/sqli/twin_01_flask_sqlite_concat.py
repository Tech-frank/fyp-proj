import sqlite3

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/users")
def get_user():
    user_id = request.args.get("id", "")
    conn = sqlite3.connect("app.db")
    row = conn.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return jsonify(row)
