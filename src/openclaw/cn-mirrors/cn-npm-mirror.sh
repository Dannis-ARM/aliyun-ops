#!/bin/bash
# 📦 NVM + npm mirror setup (idempotent)

TARGET_NODE_VERSION="24"

# Install NVM if not exists
if [ ! -s "$HOME/.nvm/nvm.sh" ]; then
    echo "📦 Installing NVM..."
    mkdir -p ~/.activate/nvm
    export NVM_NODEJS_ORG_MIRROR=https://repo.huaweicloud.com/nodejs/
    curl -o- https://gitee.com/mirrors/nvm/raw/master/install.sh | bash
fi

# Load NVM
# shellcheck disable=SC1091
[ -s "$HOME/.nvm/nvm.sh" ] && \. "$HOME/.nvm/nvm.sh"

# Install Node if not exists
if ! command -v node &> /dev/null; then
    echo "📦 Installing Node.js $TARGET_NODE_VERSION..."
    nvm install "$TARGET_NODE_VERSION" && nvm alias default "$TARGET_NODE_VERSION"
else
    echo "✅ Node $(node -v) already installed"
fi

# Force set npm mirror
echo "📦 Setting npm registry to npmmirror..."
npm config set registry https://registry.npmmirror.com/

echo "Node: $(node -v) | npm: $(npm -v) | Registry: $(npm get registry)"

# Restore official: npm config set registry https://registry.npmjs.org/
