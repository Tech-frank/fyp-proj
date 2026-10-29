import requests

TOKEN_URL = "https://oauth2.example-idp.com/oauth/token"
AUTHORIZE_URL = "https://oauth2.example-idp.com/oauth/authorize"


def exchange_code(code, client_id, client_secret):
    resp = requests.post(TOKEN_URL, data={
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
    }, timeout=10)
    return resp.json()["access_token"]
