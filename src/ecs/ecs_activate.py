"""
Aliyun ECS Instance Activation/Deployment Script
Automates initial setup: mirror config, tools, cron deployment.
"""

import sys
from pathlib import Path
from common.logging import setup_logging
from common.ssh import ProxyConfig, SSHClientV2
from cfgs import (
    ALIYUN_OPS_KEY_DEFAULT,
    ALIYUN_OPS_USER,

    ECS_HOST,
    SSH_KEY_DEFAULT,
    DEFAULT_ADMIN_USER,
    ACTIVATE_LOG_FILE_NAME,
)
from _create_aliops_user import create_aliops_user

# Setup logging
logger = setup_logging(
    name="ecs-activate", 
    verbose=True,
    log_file=Path(__file__).parent / ACTIVATE_LOG_FILE_NAME
)


def validate_scripts(scripts: list[Path]) -> None:
    """Validate required bootstrap scripts exist."""
    missing = [
        script for script in scripts if not script.exists()
    ]
    if missing:
        for f in missing:
            logger.error("Missing: %s", f)
        sys.exit(1)


def bootstrap(ssh: SSHClientV2) -> None:
    """Execute deployment steps."""
    logger.info("ECS Activation started")

    if not ssh.test_connection():
        logger.error("Cannot connect to remote host.")
        sys.exit(1)
    logger.info("Deploying to %s@%s...", ssh.user, ssh.host)

    create_aliops_user(ssh)

    # 2. Upload scripts
    local_dir = Path(__file__).parent / "bootstrap"
    activate_dir = "~/activate/bootstrap"
    
    exec_scripts = set()
    for file in Path(local_dir).glob("*.sh"):
        exec_scripts.add((file.absolute(), f"{activate_dir}/{file.name}"))

    # 3. Configure mirror & install tools
    for script_path, remote_path in exec_scripts:
        ssh.upload(script_path, remote_path)
    for script_path, remote_path in exec_scripts:
        ssh.run_sudo(f"/bin/bash {remote_path}")

    logger.info("Deployment completed successfully!")

def install_clash(ssh: SSHClientV2) -> None:
    """Execute deployment steps."""
    # https://github.com/chen08209/FlClash
    logger.info("Deploying to %s@%s...", ssh.user, ssh.host)

    local_dir = Path(__file__).parent.absolute() / "clash"
    activate_dir = "~/.activate/clash"

    exec_scripts: set[tuple[Path, str]] = {
        (local_dir / "clash-init.sh", f"{activate_dir}/clash-init.sh"),
    }

    for script_path, remote_path in exec_scripts:
        ssh.upload(script_path, remote_path)
    for script_path, remote_path in exec_scripts:
        ssh.run(f"/bin/bash {remote_path}")
    
    logger.info("Deployment completed successfully!")


def main() -> None:
    # bootstrap
    with SSHClientV2(
        logger, 
        ECS_HOST, 
        DEFAULT_ADMIN_USER, 
        SSH_KEY_DEFAULT,
        proxy=ProxyConfig("http", "localhost", 7890)
    ) as ssh_admin:
        if not ssh_admin.test_connection():
            logger.error("Cannot connect to remote host.")
            sys.exit(1)
        bootstrap(ssh_admin)

    exit(1)
    # install clash  
    with SSHClientV2(
        logger,
        ECS_HOST,
        ALIYUN_OPS_USER,
        ALIYUN_OPS_KEY_DEFAULT,
        proxy=ProxyConfig("http", "localhost", 7890),
    ) as ssh_aliops:
        if not ssh_aliops.test_connection():
            logger.error("Cannot connect to remote host.")
            sys.exit(1)
        install_clash(ssh_aliops)

if __name__ == "__main__":
    main()
