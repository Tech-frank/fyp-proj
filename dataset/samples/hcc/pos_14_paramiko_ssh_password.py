import paramiko


def run_remote(command, host="10.0.0.15"):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username="deploy", password="D3ploy!Server#1")
    _, stdout, _ = client.exec_command(command)
    output = stdout.read().decode()
    client.close()
    return output
