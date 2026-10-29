import requests


def is_up(url):
    try:
        return requests.head(url, timeout=3).status_code < 400
    except requests.RequestException:
        return False
