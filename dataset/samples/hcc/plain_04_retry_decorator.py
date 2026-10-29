import functools
import time


def retry(times=3, delay=0.5):
    def decorate(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return fn(*args, **kwargs)
                except ConnectionError:
                    if attempt == times - 1:
                        raise
                    time.sleep(delay * 2 ** attempt)
        return wrapper
    return decorate
