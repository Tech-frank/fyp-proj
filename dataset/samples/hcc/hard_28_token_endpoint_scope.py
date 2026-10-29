token_scope = "read:invoices write:invoices"
client_id = "invoice-dashboard"


def token_request_body(client_secret):
    return {"grant_type": "client_credentials", "scope": token_scope,
            "client_id": client_id, "client_secret": client_secret}
