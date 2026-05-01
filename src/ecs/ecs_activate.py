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
from ecs._create_aliops_user import create_aliops_user
import utils

# Setup logging
logger = setup_logging(
    name="ecs-activate", 
    verbose=True,
    log_file=Path(__file__).parent / ACTIVATE_LOG_FILE_NAME
)


def bootstrap(ssh: SSHClientV2) -> None:
    create_aliops_user(ssh)
    success = utils.activate_execute_script(
        ssh,
        Path(__file__).parent.absolute() / "bootstrap",
        "~/.activate/sudo-bootstrap",
        "*.sh",
        sudo=True
    )

    if success:
        logger.info("Deployment completed successfully!")


def clash_setup(ssh: SSHClientV2) -> None:
    success = utils.activate_execute_script(
        ssh,
        Path(__file__).parent.absolute() / "clash",
        "~/.activate/clash",
        "*.sh",
    )

    if success:
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
        clash_setup(ssh_aliops)

if __name__ == "__main__":
    main()
