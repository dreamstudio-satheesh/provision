import paramiko
import os

def _connect(vm: str):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(vm, username="root", key_filename=os.path.expanduser("~/.ssh/id_ed25519"))
    return ssh

def _run(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    if exit_status != 0:
        raise Exception(stderr.read().decode())
    return stdout.read().decode()

def upload_and_deploy(vm: str, domain: str, compose_path: str, config_path: str, env_path: str):
    remote_dir = f"/opt/mail/{domain.replace('.', '_')}"
    compose_remote = f"{remote_dir}/docker-compose.yml"
    config_remote = f"{remote_dir}/config.toml"
    env_remote = f"{remote_dir}/.env"

    ssh = _connect(vm)
    sftp = ssh.open_sftp()

    try:
        # Create remote dir
        _run(ssh, f"mkdir -p {remote_dir}")

        # Upload files
        sftp.put(compose_path, compose_remote)
        sftp.put(config_path, config_remote)
        sftp.put(env_path, env_remote)
        

        # Deploy container
        _run(ssh, f"cd {remote_dir} && docker compose up -d")

    finally:
        sftp.close()
        ssh.close()


def run_remote_command(vm: str, cmd: str):
    ssh = _connect(vm)
    try:
        return _run(ssh, cmd)
    finally:
        ssh.close()

def upload_file(vm: str, local_path: str, remote_path: str):
    ssh = _connect(vm)
    sftp = ssh.open_sftp()
    try:
        sftp.put(local_path, remote_path)
    finally:
        sftp.close()
        ssh.close()
