import boto3

access_key_label = "AWS access key ID"


def show_identity():
    sts = boto3.client("sts")
    ident = sts.get_caller_identity()
    print(f"{access_key_label}: (from environment) account={ident['Account']}")
