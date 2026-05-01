#!/bin/bash

# ─────────────────────────────────────────────────────────────────────────────
# goclaw cfgs setup - Minimalist Version
# ─────────────────────────────────────────────────────────────────────────────

set -eu

SRC="$HOME/.activate/goclaw.tar.gz"
DEST="$HOME/programs/goclaw"

# 1. Ensure directory exists
mkdir -p "$DEST"

# 2. Extract directly to destination
if [[ -f "$SRC" ]]; then
    tar -xzf "$SRC" -C "$DEST"
    echo "[$(date)] Success: Extracted to $DEST"
    # 赋予所有脚本执行权限
    chmod +x "$DEST"/*.sh
    echo "[$(date)] Success: Set execute permissions for all scripts in $DEST"
else
    echo "[$(date)] Error: $SRC not found" >&2
    exit 1
fi

echo "🚀 Installing goclaw systemd user service..."

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# 1. 赋予执行权限
chmod +x "$SCRIPT_DIR/deploy_goclaw.sh"
echo "✅ Set execute permission for deploy_goclaw.sh"

# 2. 创建用户systemd目录
mkdir -p ~/.config/systemd/user
echo "✅ Created systemd user directory"

# 3. 复制服务文件
cp "$SCRIPT_DIR/goclaw.service" ~/.config/systemd/user/
echo "✅ Copied service file to systemd directory"

# 4. 重载systemd配置
systemctl --user daemon-reload
echo "✅ Reloaded systemd user daemon"

# 5. 启用并重启服务
echo "🔄 Applying service configuration and restarting..."
systemctl --user enable goclaw.service
systemctl --user restart goclaw.service
echo "✅ goclaw service is enabled and has been restarted to apply changes."

# 6. 开启用户linger（退出登录后服务仍运行）
loginctl enable-linger $USER
echo "✅ Enabled linger for user $USER"

echo -e "\n🎉 Goclaw deployment and service installation completed!"
echo -e "\n📋 Useful commands:"
echo "  Check status: systemctl --user status goclaw.service"
echo "  View logs:    journalctl --user -u goclaw.service -f"
echo "  Restart:      systemctl --user restart goclaw.service"
echo "  Stop:         systemctl --user stop goclaw.service"

echo -e "\n🔍 Verifying service status..."
systemctl --user status goclaw.service --no-pager
