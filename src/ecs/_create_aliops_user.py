"""
Create aliops User on Debian 12 ECS
Platform: Windows (Python 3.8+)

This script creates a new user 'aliops' on a remote Debian 12 instance:
    1. Generate local SSH key pair for aliops user
    2. Upload bash script to remote host
    3. Execute script to create user with public key authentication

Author: Dannis-ARM
"""

import sys
from pathlib import Path

from common import SSHKeyManager, SSHClientV2
from cfgs import (
    ACTIVATE_LOG_FILE_NAME,
    ALIYUN_OPS_USER,
    ALIYUN_OPS_KEY_DEFAULT,
    SSH_KEY_TYPE,
    SSH_KEY_COMMENT,
    REMOTE_SCRIPT_PATH,
)
from common.logging import setup_logging

logger = setup_logging(
    name=__file__, 
    verbose=True,
    log_file=Path(__file__).parent / ACTIVATE_LOG_FILE_NAME
)

# ============================================================
# Steps
# ============================================================
def _generate_ssh_key(logger, aliops_key_path: Path) -> tuple[Path, str]:
    """Generate SSH key for aliops user."""
    logger.info("Generating SSH key for %s...", ALIYUN_OPS_USER)
    key_manager = SSHKeyManager(logger)
    ssh_key = key_manager.generate(
        aliops_key_path,
        key_type=SSH_KEY_TYPE,
        comment=SSH_KEY_COMMENT
    )
    public_key = key_manager.read_public_key(ssh_key)
    return ssh_key, public_key


def _upload_bootstrap_script(ssh: SSHClientV2, logger) -> None:
    """Upload bootstrap script to remote host."""
    logger.info("Uploading bootstrap script...")
    bootstrap_script = Path(__file__).parent / "_create_aliops_user.sh"

    if not bootstrap_script.exists():
        logger.error("Bootstrap script not found: %s", bootstrap_script)
        sys.exit(1)

    ssh.upload(bootstrap_script, REMOTE_SCRIPT_PATH)


def _create_user(ssh: SSHClientV2, logger, public_key: str) -> None:
    """Create aliops user on remote host."""
    logger.info("Creating %s user on remote host...", ALIYUN_OPS_USER)
    ssh.run(f"chmod +x {REMOTE_SCRIPT_PATH} && sudo {REMOTE_SCRIPT_PATH} '{public_key}'")


# ============================================================
# Main Deployment Function
# ============================================================
def create_aliops_user(ssh: SSHClientV2) -> tuple[Path, bool]:
    """
    Create aliops user on remote host via SSH connection.
    
    Args:
        ssh: Pre-configured SSH client connected to admin user
        
    Returns:
        tuple: (ssh_key_path, login_test_success)
    """
    logger = ssh.logger
    logger.info("=" * 60)
    logger.info("Creating %s User on %s@%s", ALIYUN_OPS_USER, ssh.user, ssh.host)
    logger.info("=" * 60)

    # Step 1: Generate SSH key
    logger.info("")
    logger.info("Step 1/3: Generating SSH key for %s...", ALIYUN_OPS_USER)
    ssh_key, public_key = _generate_ssh_key(logger, ALIYUN_OPS_KEY_DEFAULT)

    # Step 2: Upload bootstrap script
    logger.info("")
    logger.info("Step 2/3: Uploading bootstrap script...")
    _upload_bootstrap_script(ssh, logger)

    # Step 3: Create aliops user
    logger.info("")
    logger.info("Step 3/3: Creating %s user on remote host...", ALIYUN_OPS_USER)
    _create_user(ssh, logger, public_key)

    # Test login
    success = ssh.test_login()

    logger.info("")
    logger.info("=" * 60)
    if success:
        logger.info("SUCCESS! %s user created and configured!", ALIYUN_OPS_USER)
        logger.info("Login command: ssh -i %s %s@%s", ssh_key, ALIYUN_OPS_USER, ssh.host)
    else:
        logger.warning("SSH login test failed, but user may still be usable.")
        logger.warning("Try: ssh -i %s %s@%s", ssh_key, ALIYUN_OPS_USER, ssh.host)

    logger.info("")
    logger.info("Public key (%s):", ssh_key.with_suffix('.pub'))
    logger.info("  %s", public_key)

    return ssh_key, success

