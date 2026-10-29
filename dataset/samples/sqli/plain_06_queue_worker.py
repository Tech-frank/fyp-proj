import queue
import threading

jobs = queue.Queue()


def worker():
    while True:
        job = jobs.get()
        try:
            job()
        finally:
            jobs.task_done()


threading.Thread(target=worker, daemon=True).start()
