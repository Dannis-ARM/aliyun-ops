#!/bin/bash
set -e  # 任一命令失败则退出

DEST="$HOME/programs/goclaw"
cd "$DEST" 
chmod +x ./goclaw


# Prepare skills environment 
export NVM_DIR="$HOME/.nvm"
if [ -s "$NVM_DIR/nvm.sh" ]; then
    source "$NVM_DIR/nvm.sh"
fi

# PATH for nodejs 
NPM_GLOBAL_BIN="$(npm config get prefix)/bin"
export PATH="$NPM_GLOBAL_BIN:$PATH"

# 加载环境变量并使用 exec 替换当前 shell 进程
# 这样 systemd 就能直接管理 goclaw 进程，而不是管理 shell 脚本
if [ -f .env.local ]; then
    source .env.local
fi

./goclaw migrate up
exec ./goclaw