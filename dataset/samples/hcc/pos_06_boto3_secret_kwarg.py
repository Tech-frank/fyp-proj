import boto3


def upload_backup(path, bucket="nightly-backups"):
    s3 = boto3.client(
        "s3",
        region_name="eu-west-1",
        aws_access_key_id="AKIAIOSFODNN7EXAMPLE",
        aws_secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    )
    s3.upload_file(path, bucket, path.split("/")[-1])
