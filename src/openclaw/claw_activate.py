"""
Download goclaw via proxy and upload to Aliyun ECS.

Usage:
    python -m src.openapi.activate
"""

import sys
from pathlib import Path

from common.downloader import FileDownloader
from common.logging import setup_logging
from common.ssh import SSHClientV2
from cfgs import (
    ALIYUN_OPS_USER,
    ECS_HOST,
    ALIYUN_OPS_KEY_DEFAULT,
)
import utils

logger = setup_logging(name="goclaw-upload")

# Download configuration
downloader = FileDownloader(timeout=60, use_clash_proxy=True)

# NOT USED
def openclaw(ssh: SSHClientV2) -> None:
    """Execute deployment steps."""
    logger.info("Deploying to %s@%s...", ssh.user, ssh.host)

    local_dir = Path(__file__).parent.absolute() / "goclaw"
    activate_dir = "~/.activate/goclaw"

    # Download file
    goclaw_url = "https://github.com/nextlevelbuilder/goclaw/releases/download/v2.67.0/goclaw-2.67.0-linux-amd64.tar.gz"
    downloaded_path = downloader.download(goclaw_url)
    
    sftp_mappings = [
        (local_dir / "deploy_goclaw.sh", f"{activate_dir}/deploy_goclaw.sh"),
        (downloaded_path, "~/goclaw-2.67.0-linux-amd64.tar.gz"),
    ]

    for script_path, remote_path in sftp_mappings:
        ssh.upload(script_path, remote_path)

    logger.info("Deployment completed successfully!")

def goclaw_setup(ssh: SSHClientV2) -> None:
    if not ssh.test_connection():
        logger.error("Cannot connect to remote host.")
        sys.exit(1)

    utils.activate_execute_script(
        ssh,
        Path(__file__).parent.absolute() / "goclaw",
        "~/.activate/goclaw",
        "deploy*.sh"
    )

def mirror_setup(ssh: SSHClientV2) -> None:
    if not ssh.test_connection():
        logger.error("Cannot connect to remote host.")
        sys.exit(1)
    
    utils.upload(
        ssh,
        Path(__file__).parent.absolute() / "cn-mirrors",
        "~/.activate/cn-mirrors",
        "*.yml"
    )

    utils.activate_execute_script(
        ssh,
        Path(__file__).parent.absolute() / "cn-mirrors",
        "~/.activate/cn-mirrors",
        "*.sh"
    )

    logger.info("install_pgvector completed successfully!")


def main():
    ssh: SSHClientV2 = SSHClientV2(
        logger, ECS_HOST, ALIYUN_OPS_USER, ALIYUN_OPS_KEY_DEFAULT
    )
    mirror_setup(ssh)

if __name__ == "__main__":
    main()
