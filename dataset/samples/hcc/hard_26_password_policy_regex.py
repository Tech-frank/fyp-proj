import re

password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{12,}$"


def meets_policy(candidate):
    return re.match(password_pattern, candidate) is not None
