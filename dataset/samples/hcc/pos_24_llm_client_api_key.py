from llm_vendor import Client

client = Client(api_key="sk-proj-Tz8Qw3Er5Ty7Ui9Op1As2Df4Gh6Jk")


def summarise(text):
    reply = client.complete(prompt=f"Summarise:\n{text}", max_tokens=200)
    return reply.text
