from ftplib import FTP


def push_export(local_path):
    with FTP("ftp.partner.example") as ftp:
        ftp.login("export_bot", "Exp0rt!Ftp2023")
        with open(local_path, "rb") as fh:
            ftp.storbinary("STOR daily.csv", fh)
