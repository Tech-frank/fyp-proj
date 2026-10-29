import os

from twilio.rest import Client

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]


def send_sms(to, body):
    client = Client(account_sid, auth_token)
    return client.messages.create(to=to, from_="+15005550006", body=body)
