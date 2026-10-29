from twilio.rest import Client

account_sid = "AC5f2e8b1d9c4a7e3f6b0d2c8a1e9f4b7d"
auth_token = "7c1e9a3f5b2d8e4a6c0f9b1d3e7a5c2f"


def send_sms(to, body):
    client = Client(account_sid, auth_token)
    return client.messages.create(to=to, from_="+15005550006", body=body)
