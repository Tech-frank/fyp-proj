from celery import Celery

app = Celery(
    "worker",
    broker="amqp://jobs:Rabb1tJobs!2024@rabbitmq.internal:5672/prod",
    backend="rpc://",
)


@app.task
def resize_image(path):
    return path
