import sendgrid
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY = "SG.k3Jd8Qp2Rw5Tz1Lm.9Xc4Vb7Nn2Mq6Ws0Ea8Rd3Tf5Gy1Hu"
sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)


def welcome(email):
    sg.send(Mail(from_email="hello@example.com", to_emails=email,
                 subject="Welcome", html_content="<p>Thanks for joining.</p>"))
