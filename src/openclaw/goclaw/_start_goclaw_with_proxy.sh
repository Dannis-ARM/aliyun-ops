#!/bin/bash
set -e  # 任一命令失败则退出

DEST="$HOME/programs/goclaw"
cd "$DEST" 
chmod +x ./goclaw

# 加载环境变量并使用 exec 替换当前 shell 进程
# 这样 systemd 就能直接管理 goclaw 进程，而不是管理 shell 脚本
if [ -f .env.local ]; then
    source .env.local
fi

export HTTPS_PROXY=http://127.0.0.1:7890
export HTTP_PROXY=http://127.0.0.1:7890
curl -I -s https://www.google.com
exec ./goclaw