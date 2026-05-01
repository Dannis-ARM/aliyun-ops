from pathlib import Path

from common import setup_logging
from common.ssh import SSHClientV2

logger = setup_logging(__name__)

def validate_scripts(scripts: list[Path]) -> None:
    """Validate required bootstrap scripts exist."""
    missing = [
        script for script in scripts if not script.exists()
    ]
    if missing:
        for f in missing:
            logger.error("Missing: %s", f)
            raise FileNotFoundError(f)

def activate_execute_script(
    ssh: SSHClientV2, local_dir: Path, activate_dir: str, glob_pattern: str = "*.sh", sudo=False
) -> None:
    exec_scripts = set()
    for file in Path(local_dir).glob(glob_pattern):
        exec_scripts.add((file.absolute(), f"{activate_dir}/{file.name}"))
    for script_path, remote_path in exec_scripts:
        ssh.upload(script_path, remote_path)

    for script_path, remote_path in exec_scripts:
        if sudo:
            ssh.run_sudo(f"/bin/bash {remote_path}")
        else:
            ssh.run(f"/bin/bash {remote_path}")

def upload(
    ssh: SSHClientV2, local_dir: Path, activate_dir: str, glob_pattern: str = "*.yml"
) -> None:
    sftp_mappings = set()
    for file in Path(local_dir).absolute().glob(glob_pattern):
        sftp_mappings.add((file.absolute(), f"{activate_dir}/{file.name}"))
    for script_path, remote_path in sftp_mappings:
        ssh.upload(script_path, remote_path)
