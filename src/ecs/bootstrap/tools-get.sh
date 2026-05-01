#!/bin/bash
# =============================================================================
# Debian/Ubuntu System Initialization Script
# Version: 2.0
# Improvement: Centralized installation, verification, and non-interactive setup.
# =============================================================================

set -euo pipefail

# 1. 环境变量配置
export DEBIAN_FRONTEND=noninteractive

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%dT%H:%M:%S')] INFO:${NC} $1"
}

error_exit() {
    echo -e "${RED}[$(date +'%Y-%m-%dT%H:%M:%S')] ERROR:${NC} $1" >&2
    exit 1
}

# 2. 权限校验
[[ $EUID -ne 0 ]] && error_exit "This script must be run as root/sudo."

# 3. 核心安装逻辑
main() {
    log "Starting system initialization..."

    # 更新索引 (仅执行一次，减少 IO 和带宽消耗)
    log "Updating apt package index..."
    apt-get update -y || error_exit "Failed to update apt index."

    # 定义安装包列表 (按功能分类，便于维护)
    local sys_tools=(
        net-tools
        cron
        htop
        sysstat
        zip
        unzip
        git
        make
        jq
    )
    
    local network_tools=(
        netcat-openbsd
        mtr-tiny
    )
    
    local podman_stack=(
        fuse-overlayfs
        podman
        podman-docker
    )

    log "Installing system and network tools..."
    # 一并安装，利用 apt 的并行依赖解析，效率更高
    apt-get install -y "${sys_tools[@]}" "${network_tools[@]}" "${podman_stack[@]}" || \
        error_exit "Failed to install package list."

    # 4. 系统配置
    log "Configuring system timezone..."
    timedatectl set-timezone Asia/Shanghai

    # 5. 服务状态检查 (针对关键服务)
    log "Ensuring services are enabled..."
    systemctl enable --now cron || log "Warning: Failed to start cron."

    # 6. 环境清理
    log "Cleaning up apt cache..."
    apt-get autoremove -y && apt-get clean

    log "System initialization completed successfully!"
}

# 执行主函数
main "$@"