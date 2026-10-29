import os

from slack_sdk import WebClient

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
client = WebClient(token=SLACK_BOT_TOKEN)


def notify(channel, text):
    client.chat_postMessage(channel=channel, text=text)
