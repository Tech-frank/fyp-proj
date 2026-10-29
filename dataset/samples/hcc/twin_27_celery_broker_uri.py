import os

from celery import Celery

app = Celery(
    "worker",
    broker=os.environ["CELERY_BROKER_URL"],
    backend="rpc://",
)


@app.task
def resize_image(path):
    return path
