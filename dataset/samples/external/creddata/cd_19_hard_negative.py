def _auth_method(self, url):
    from requests.auth import HTTPBasicAuth, HTTPDigestAuth

    if self.auth:
        if self.ask_password and self.password is None:
            self.password = ask_password(urlparse(url).hostname, self.user)
        if self.auth == "basic":
            return HTTPBasicAuth(self.user, self.password)
        if self.auth == "digest":
            return HTTPDigestAuth(self.user, self.password)
        if self.auth == "custom" and self.custom_auth_header:
            self.headers.update({self.custom_auth_header: self.password})
    return None
