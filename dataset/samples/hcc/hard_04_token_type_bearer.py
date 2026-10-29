def build_auth_header(access):
    token_type = "Bearer"
    return {"Authorization": f"{token_type} {access}"}
