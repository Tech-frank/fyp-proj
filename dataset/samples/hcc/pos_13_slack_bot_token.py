from slack_sdk import WebClient

SLACK_BOT_TOKEN = "xoxb-2871634592-5523149870-q8RzT4vW6yA1"
client = WebClient(token=SLACK_BOT_TOKEN)


def notify(channel, text):
    client.chat_postMessage(channel=channel, text=text)
