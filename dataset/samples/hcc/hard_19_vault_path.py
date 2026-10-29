import hvac

vault_secret_path = "secret/data/billing/stripe"


def read_billing_secret(client: hvac.Client):
    response = client.secrets.kv.v2.read_secret_version(path=vault_secret_path)
    return response["data"]["data"]["api_key"]
