import os

import requests


def trigger_build(job):
    url = f"https://ci.example.com/job/{job}/build"
    resp = requests.post(url, auth=("ci-bot", os.environ["CI_API_TOKEN"]), timeout=20)
    return resp.status_code == 201
