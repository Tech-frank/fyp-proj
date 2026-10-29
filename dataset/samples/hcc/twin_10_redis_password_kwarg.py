import os

import redis

cache = redis.Redis(
    host="cache.internal",
    port=6379,
    db=2,
    password=os.environ.get("REDIS_PASSWORD"),
    decode_responses=True,
)


def remember(key, value, ttl=300):
    cache.setex(key, ttl, value)
