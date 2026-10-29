import os
import subprocess

pwd_command = "pwd"


def where_am_i():
    out = subprocess.run([pwd_command], capture_output=True, text=True)
    return out.stdout.strip() or os.getcwd()
