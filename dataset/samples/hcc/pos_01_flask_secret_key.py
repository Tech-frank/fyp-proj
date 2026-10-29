from flask import Flask

app = Flask(__name__)
app.config["DEBUG"] = False
SECRET_KEY = "f9c2e1a7b44d0e3c8a61f5b29d7e0c13"
app.secret_key = SECRET_KEY


@app.route("/health")
def health():
    return {"status": "ok"}
