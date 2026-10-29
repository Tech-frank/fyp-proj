import os

from llm_vendor import Client

client = Client(api_key=os.environ["LLM_API_KEY"])


def summarise(text):
    reply = client.complete(prompt=f"Summarise:\n{text}", max_tokens=200)
    return reply.text
