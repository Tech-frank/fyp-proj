import os

from flask import Flask

app = Flask(__name__)
app.config["DEBUG"] = False
SECRET_KEY = os.environ["FLASK_SECRET_KEY"]
app.secret_key = SECRET_KEY


@app.route("/health")
def health():
    return {"status": "ok"}
