import os
import subprocess

REGISTRY = "registry.example.com"
REGISTRY_TOKEN = os.environ["REGISTRY_TOKEN"]


def docker_login():
    subprocess.run(
        ["docker", "login", REGISTRY, "-u", "ci", "--password-stdin"],
        input=REGISTRY_TOKEN.encode(),
        check=True,
    )
