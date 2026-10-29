import subprocess

REGISTRY = "registry.example.com"
REGISTRY_TOKEN = "glpat-Xy9Zq2Wv5Ut8Sr1Qp4On"


def docker_login():
    subprocess.run(
        ["docker", "login", REGISTRY, "-u", "ci", "--password-stdin"],
        input=REGISTRY_TOKEN.encode(),
        check=True,
    )
