"""
Configuration for ECS management scripts.
All configurable constants should be defined here.
"""

import os
from pathlib import Path

# ============================================================
# SSH Configuration
# ============================================================
# Default admin SSH key path on Windows
SSH_KEY_DEFAULT = Path(
    os.environ.get("USERPROFILE", "~")).expanduser() / ".ssh" / "ali-ecs-key.pem"

# Default admin user for remote operations
DEFAULT_ADMIN_USER = "debian"

# Default aliops user (the user to create)
ALIYUN_OPS_USER = "aliops"

# Default aliops SSH key path
ALIYUN_OPS_KEY_DEFAULT = Path(os.environ.get("USERPROFILE", "~")).expanduser() / ".ssh" / "aliops-key"

# SSH key type
SSH_KEY_TYPE = "ed25519"

# SSH key comment
SSH_KEY_COMMENT = "aliops@aliyun-ecs"

# ============================================================
# ECS Target Host
# ============================================================
# Default ECS host for goclaw download and upload
ECS_HOST = "ecs-mini.aliyun.gilded-age.cn"

# Default ECS user (aliops user)
ECS_USER = ALIYUN_OPS_USER

# ============================================================
# Bootstrap Scripts
# ============================================================
# Local bootstrap directory
BOOTSTRAP_DIR = Path(__file__).parent / "ecs" / "bootstrap"

# Remote bootstrap script path (for create_aliops_user.py)
REMOTE_SCRIPT_PATH = "~/create_aliops_user.sh"

# ============================================================
# Activate Scripts (for activate.py)
# ============================================================
# Remote activate directory
REMOTE_ACTIVATE_DIR = "~/activate"

# Remote bootstrap subdirectory
REMOTE_BOOTSTRAP_DIR = "~/activate/bootstrap/"

# Scripts to deploy during activation
# Format: (local_filename, remote_path)
ACTIVATE_SCRIPTS_TO_DEPLOY = [
    ("debian-init.sh", REMOTE_BOOTSTRAP_DIR),
    ("tools-install.sh", REMOTE_BOOTSTRAP_DIR),
    ("reboot/sys-cron", REMOTE_BOOTSTRAP_DIR),
]

# Remote script paths (for activate.py)
REMOTE_DEBIAN_INIT = f"{REMOTE_BOOTSTRAP_DIR}debian-init.sh"
REMOTE_TOOLS_INSTALL = f"{REMOTE_BOOTSTRAP_DIR}tools-install.sh"
REMOTE_SYS_CRON = f"{REMOTE_BOOTSTRAP_DIR}sys-cron"

# Cron deployment target
CRON_TARGET_PATH = "/etc/cron.d/sys-cron"

# ============================================================
# Logging
# ============================================================
# Default log file name (for create_aliops_user.py)
LOG_FILE_NAME = "create_aliops.log"

# Default log file name (for activate.py)
ACTIVATE_LOG_FILE_NAME = "activate.log"

# ============================================================
# Remote Paths
# ============================================================
# Remote home directory path
REMOTE_HOME = "~"

# Remote bin directory path
REMOTE_BIN = "~/bin"
