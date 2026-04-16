#!/bin/bash
# =============================================================================
# Script: setup_swap.sh
# Description: Idempotent swap file creation (1GB) for Debian/Ubuntu.
# =============================================================================

set -euo pipefail

SWAP_PATH="/swapfile"
SWAP_SIZE_MB=1024

log_info() { echo -e "\033[0;32m[INFO]\033[0m $1"; }
log_warn() { echo -e "\033[1;33m[WARN]\033[0m $1"; }

# 1. 创建 Swap 文件 (检查是否存在且大小正确)
if [[ -f "$SWAP_PATH" ]]; then
    log_warn "$SWAP_PATH already exists. Skipping creation."
else
    log_info "Creating $SWAP_SIZE_MB MB swap file at $SWAP_PATH..."
    # 使用 fallocate 比 dd 更快且对磁盘友好
    fallocate -l ${SWAP_SIZE_MB}M "$SWAP_PATH" || dd if=/dev/zero of="$SWAP_PATH" bs=1M count=$SWAP_SIZE_MB
    
    log_info "Setting permissions to 600..."
    chmod 600 "$SWAP_PATH"
    
    log_info "Formatting as swap..."
    mkswap "$SWAP_PATH"
fi

# 2. 启用 Swap (检查是否已激活)
if swapon --show | grep -q "$SWAP_PATH"; then
    log_warn "Swap is already active on $SWAP_PATH."
else
    log_info "Activating swap..."
    swapon "$SWAP_PATH"
fi

# 3. 持久化配置 (检查 /etc/fstab 是否已存在记录)
FSTAB_ENTRY="$SWAP_PATH none swap sw 0 0"
if grep -Fxq "$FSTAB_ENTRY" /etc/fstab; then
    log_warn "Swap entry already exists in /etc/fstab."
else
    log_info "Adding swap entry to /etc/fstab..."
    # 备份并追加
    cp /etc/fstab "/etc/fstab.bak.$(date +%F)"
    echo "$FSTAB_ENTRY" | tee -a /etc/fstab
fi

# 4. 输出当前状态
log_info "Current swap status:"
swapon --show
free -h