import boto3


def upload_backup(path, bucket="nightly-backups"):
    # Credentials come from the default AWS chain (env vars, profile or role).
    s3 = boto3.client("s3", region_name="eu-west-1")
    s3.upload_file(path, bucket, path.split("/")[-1])
