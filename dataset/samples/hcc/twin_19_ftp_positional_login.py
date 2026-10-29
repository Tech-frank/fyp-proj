import os
from ftplib import FTP


def push_export(local_path):
    with FTP("ftp.partner.example") as ftp:
        ftp.login(os.environ["FTP_USER"], os.environ["FTP_PASSWORD"])
        with open(local_path, "rb") as fh:
            ftp.storbinary("STOR daily.csv", fh)
