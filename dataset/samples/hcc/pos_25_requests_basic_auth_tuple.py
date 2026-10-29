import requests


def trigger_build(job):
    url = f"https://ci.example.com/job/{job}/build"
    resp = requests.post(url, auth=("ci-bot", "11a9f8e2c7b6d5a4e3f2c1b0"), timeout=20)
    return resp.status_code == 201
