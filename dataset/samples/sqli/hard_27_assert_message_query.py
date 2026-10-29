def check_migration(cursor):
    cursor.execute("SELECT COUNT(*) FROM schema_version")
    version = cursor.fetchone()[0]
    assert version >= 12, f"expected schema >= 12, SELECT returned {version}"
