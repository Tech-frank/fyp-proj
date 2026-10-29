import json
from pathlib import Path

DEFAULTS = {"page_size": 50, "theme": "light"}


def load_settings(path="settings.json"):
    file = Path(path)
    if not file.exists():
        return dict(DEFAULTS)
    return {**DEFAULTS, **json.loads(file.read_text(encoding="utf-8"))}
