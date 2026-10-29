import redis

cache = redis.Redis(
    host="cache.internal",
    port=6379,
    db=2,
    password="c4che-R3dis-9xQ",
    decode_responses=True,
)


def remember(key, value, ttl=300):
    cache.setex(key, ttl, value)
