import boto3

SECRET_NAME = "prod/payments/api"


def get_payment_secret():
    client = boto3.client("secretsmanager", region_name="eu-west-1")
    return client.get_secret_value(SecretId=SECRET_NAME)["SecretString"]
