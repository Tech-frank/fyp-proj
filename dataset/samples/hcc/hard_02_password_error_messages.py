PASSWORD_TOO_SHORT = "Password must be at least 12 characters long."
PASSWORD_NO_DIGIT = "Password must contain at least one digit."


def validate(password):
    errors = []
    if len(password) < 12:
        errors.append(PASSWORD_TOO_SHORT)
    if not any(c.isdigit() for c in password):
        errors.append(PASSWORD_NO_DIGIT)
    return errors
