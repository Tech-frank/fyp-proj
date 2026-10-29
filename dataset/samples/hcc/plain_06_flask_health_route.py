from flask import Flask, jsonify

app = Flask(__name__)
VERSION = "2.4.1"


@app.route("/version")
def version():
    return jsonify(version=VERSION)
