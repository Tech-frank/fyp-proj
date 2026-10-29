from collections import Counter

auth_failures = Counter()
AUTH_LOCKOUT_MESSAGE = "Too many failed attempts. Try again in 15 minutes."


def record_failure(username):
    auth_failures[username] += 1
    return auth_failures[username] >= 5
