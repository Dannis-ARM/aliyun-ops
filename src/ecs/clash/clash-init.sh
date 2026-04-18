#!/bin/bash
# https://github.com/nelvko/clash-for-linux-install?tab=readme-ov-file

# 配置项
SET_DIR="$HOME/.activate"
INSTALL_DIR="$HOME/clashctl"
REPO_URL="https://gh-proxy.org/https://github.com/nelvko/clash-for-linux-install.git"

# 严格模式与日志
set -euo pipefail

log() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] $1"
}

# 环境准备
mkdir -p "${SET_DIR}"
cd "${SET_DIR}" || { log "Failed to enter ${SET_DIR}"; exit 1; }

# 安装逻辑
if [[ ! -d "${INSTALL_DIR}" ]]; then
    log "Starting to clone repository..."
    # 使用显式目录名，确保逻辑闭环
    git clone --branch master --depth 1 "${REPO_URL}" "${INSTALL_DIR}"
    
    log "Running installation script..."
    # 使用子 Shell 运行安装，避免污染当前进程的工作目录
    (
        cd "${INSTALL_DIR}" || exit 1
        bash install.sh
    )
    log "Installation completed."
else
    log "Directory ${INSTALL_DIR} already exists. Skipping clone."
fi