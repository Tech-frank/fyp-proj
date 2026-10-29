import os

import ldap


def find_user(uid):
    conn = ldap.initialize("ldap://directory.corp.example")
    conn.simple_bind_s("cn=admin,dc=corp,dc=example", os.environ["LDAP_BIND_PASSWORD"])
    return conn.search_s("ou=people,dc=corp,dc=example", ldap.SCOPE_SUBTREE, f"(uid={uid})")
