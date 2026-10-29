AUTH_BACKEND = "ldap"
auth_method = "kerberos"
session_token_cookie = "sid"


def describe_auth():
    return f"backend={AUTH_BACKEND}, method={auth_method}, cookie={session_token_cookie}"
