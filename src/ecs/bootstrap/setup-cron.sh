#!/bin/bash

set -euo pipefail

# 使用 tee 命令正确写入系统级 cron 文件
echo "0 1 * * 1 root /sbin/shutdown -r now" | sudo tee /etc/cron.d/sys-cron > /dev/null

# 确保所有权和权限（正如你所写的）
sudo chown root:root /etc/cron.d/sys-cron
sudo chmod 644 /etc/cron.d/sys-cron