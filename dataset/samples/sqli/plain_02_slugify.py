import re


def slugify(title):
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower())
    return slug.strip("-")
