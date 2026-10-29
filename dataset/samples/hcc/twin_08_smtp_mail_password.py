import os
import smtplib
from email.message import EmailMessage

SMTP_HOST = "smtp.mailhost.example"
mail_user = "alerts@example.com"
mail_password = os.environ["ALERTS_SMTP_PASSWORD"]


def send_alert(subject, body, to):
    msg = EmailMessage()
    msg["Subject"], msg["From"], msg["To"] = subject, mail_user, to
    msg.set_content(body)
    with smtplib.SMTP_SSL(SMTP_HOST, 465) as smtp:
        smtp.login(mail_user, mail_password)
        smtp.send_message(msg)
