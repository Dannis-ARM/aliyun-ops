#!/bin/bash

# ===================== 配置项 =====================
# 选择镜像源（取消注释一个，注释其他）
# MIRROR_URL="https://pypi.tuna.tsinghua.edu.cn/simple"  # 清华镜像
MIRROR_URL="https://mirrors.aliyun.com/pypi/simple/"     # 阿里云（推荐，最稳定）
# MIRROR_URL="https://pypi.doubanio.com/simple"           # 豆瓣镜像
# ==================================================

# 配置文件路径（Linux/macOS 通用）
PIP_CONFIG="$HOME/.config/pip/pip.conf"

# 创建配置目录
mkdir -p "$(dirname "$PIP_CONFIG")"

# 写入镜像配置
cat > "$PIP_CONFIG" << EOF
[global]
index-url = $MIRROR_URL
trusted-host = $(echo $MIRROR_URL | awk -F[/:] '{print $4}')
EOF

# 提示完成
echo "✅ Python 镜像源已配置完成！"
echo "📄 配置文件路径：$PIP_CONFIG"
echo "🔗 当前镜像地址：$MIRROR_URL"