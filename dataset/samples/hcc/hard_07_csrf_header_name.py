CSRF_TOKEN_HEADER = "X-CSRFToken"
CSRF_COOKIE_NAME = "csrftoken"


def attach_csrf(session, headers):
    headers[CSRF_TOKEN_HEADER] = session.cookies.get(CSRF_COOKIE_NAME, "")
    return headers
