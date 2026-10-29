AUTH_HEADER = "Authorization"
api_key_header = "X-API-Key"


def extract_key(request):
    return request.headers.get(api_key_header) or request.headers.get(AUTH_HEADER, "")
