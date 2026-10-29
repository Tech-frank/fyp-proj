import yaml


def read_pipeline(path):
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh).get("stages", [])
