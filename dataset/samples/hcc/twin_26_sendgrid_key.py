import os

import sendgrid
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]
sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)


def welcome(email):
    sg.send(Mail(from_email="hello@example.com", to_emails=email,
                 subject="Welcome", html_content="<p>Thanks for joining.</p>"))
