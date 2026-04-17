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

logger = setup_logging(name=__file__)

downloader = FileDownloader(timeout=60, use_clash_proxy=True)

def mirror_setup(ssh: SSHClientV2) -> None:
    utils.activate_execute_script(
        ssh,
        Path(__file__).parent.absolute() / "cn-mirrors",
        "~/.activate/cn-mirrors",
        "*.sh"
    )

def pgvector_setup(ssh: SSHClientV2) -> None:
    utils.upload(
        ssh,
        Path(__file__).parent.absolute() / "goclaw" / "pgvector",
        "~/.activate/pgvector",
        "*.yml"
    )

    utils.activate_execute_script(
        ssh,
        Path(__file__).parent.absolute() / "goclaw" / "pgvector",
        "~/.activate/pgvector",
        "*.sh"
    )
    logger.info("install_pgvector completed successfully!")


def goclaw_setup(ssh: SSHClientV2) -> None:
    # download go binary
    goclaw_url = "https://github.com/nextlevelbuilder/goclaw/releases/download/v3.8.5/goclaw-3.8.5-linux-amd64.tar.gz"
    downloaded_path = downloader.download(goclaw_url)
    ssh.upload(downloaded_path, "~/.activate/goclaw.tar.gz")

    utils.activate_execute_script(
        ssh,
        Path(__file__).parent.absolute() / "goclaw",
        "~/.activate/goclaw",
        "deploy*.sh"
    )

def main():
    ssh: SSHClientV2 = SSHClientV2(
        logger, ECS_HOST, ALIYUN_OPS_USER, ALIYUN_OPS_KEY_DEFAULT
    )
    if not ssh.test_connection():
        logger.error("Cannot connect to remote host.")
        sys.exit(1)

    # mirror_setup(ssh)
    # pgvector_setup(ssh)
    goclaw_setup(ssh)

if __name__ == "__main__":
    main()
