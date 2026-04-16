from pathlib import Path
import sys

from common import setup_logging
from common.ssh import SSHClientV2

logger = setup_logging(__name__)

def install_pgvector(ssh: SSHClientV2, local_dir: Path, activate_dir: str) -> None:
    # ssh: SSHClientV2 = SSHClientV2(logger, ECS_HOST, DEFAULT_ADMIN_USER, SSH_KEY_DEFAULT)
    if not ssh.test_connection():
        logger.error("Cannot connect to remote host.")
        sys.exit(1)

    sftp_mappings = set()
    for file in Path(local_dir).glob("*.yml"):
        sftp_mappings.add((file.absolute(), f"{activate_dir}/{file.name}"))
    for script_path, remote_path in sftp_mappings:
        ssh.upload(script_path, remote_path)

    exec_scripts = set()
    for file in Path(local_dir).glob("*.sh"):
        exec_scripts.add((file.absolute(), f"{activate_dir}/{file.name}"))
    for script_path, remote_path in exec_scripts:
        ssh.upload(script_path, remote_path)
    for script_path, remote_path in exec_scripts:
        ssh.run(f"/bin/bash {remote_path}")

    logger.info("install_pgvector completed successfully!")

def activate_execute_script(ssh: SSHClientV2, local_dir: Path, activate_dir: str, glob_pattern: str = "*.sh") -> None:
    exec_scripts = set()
    for file in Path(local_dir).glob(glob_pattern):
        exec_scripts.add((file.absolute(), f"{activate_dir}/{file.name}"))
    for script_path, remote_path in exec_scripts:
        ssh.upload(script_path, remote_path)
    for script_path, remote_path in exec_scripts:
        ssh.run(f"/bin/bash {remote_path}")

def upload(ssh: SSHClientV2, local_dir: Path, activate_dir: str, glob_pattern: str = "*.yml") -> None:
    sftp_mappings = set()
    for file in Path(local_dir).absolute().glob(glob_pattern):
        sftp_mappings.add((file.absolute(), f"{activate_dir}/{file.name}"))
    for script_path, remote_path in sftp_mappings:
        ssh.upload(script_path, remote_path)
