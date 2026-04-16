#!/bin/bash

set -euo pipefail

export UV_INSTALLER_GITHUB_BASE_URL="https://ghfast.top/https://github.com"
[[ ! -f /home/aliops/.local/bin/uv ]] && curl -LsSf https://astral.sh/uv/install.sh | sh

# setup uv mirrors
mkdir -p ~/.config/uv
cat > ~/.config/uv/uv.toml << 'EOF'
# 阿里云 Python 镜像（加速安装 Python 本体）
python-install-mirror = "https://registry.npmmirror.com/-/binary/python-build-standalone/"

# 清华 PyPI 镜像（加速 pip 包）
[[index]]
url = "https://pypi.tuna.tsinghua.edu.cn/simple/"
default = true
EOF

. ~/.bashrc
uv python install 3.14