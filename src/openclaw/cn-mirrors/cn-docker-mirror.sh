#!/bin/bash
set -euo pipefail

# 国内镜像源配置（Podman不支持带https://前缀，直接写域名）
DOCKER_MIRRORS=(
    "6l8h60n8.mirror.aliyuncs.com"
    "docker.m.daocloud.io"
    "dockerproxy.com"
    "mirror.baidubce.com"
    "docker.nju.edu.cn"
)

# Registry配置列表：prefix, mirror_url, config_index（镜像地址不带https://前缀）
REGISTRIES=(
    "quay.io|quay.nju.edu.cn|02"
    "gcr.io|gcr.nju.edu.cn|03"
    "k8s.gcr.io|k8s-gcr.nju.edu.cn|04"
)

echo "🚀 Setting up container registry mirrors (user-level, no root required)..."

# ------------------------------
# 生成Registry配置公共函数
# ------------------------------
generate_registry_config() {
    local prefix=$1
    local mirror=$2
    local unqualified_search=${3:-false}
    
    cat << EOF
[[registry]]
prefix = "${prefix}"
location = "${prefix}"
unqualified-search = ${unqualified_search}

[[registry.mirror]]
location = "${mirror}"
insecure = false
EOF
}

# ------------------------------
# Podman 配置
# ------------------------------
if command -v podman &> /dev/null; then
    echo "📦 Detected Podman, configuring registry mirrors..."
    PODMAN_REGISTRY_DIR="$HOME/.config/containers/registries.conf.d"
    mkdir -p "${PODMAN_REGISTRY_DIR}"

    # Docker Hub 镜像配置
    echo "🔧 Configuring Docker Hub mirrors..."
    cat > "${PODMAN_REGISTRY_DIR}/00-docker-io-mirror.conf" << EOF
unqualified-search-registries = ["docker.io"]

[[registry]]
prefix = "docker.io"
location = "docker.io"
unqualified-search = true
EOF
    for mirror in "${DOCKER_MIRRORS[@]}"; do
        echo "[[registry.mirror]]" >> "${PODMAN_REGISTRY_DIR}/00-docker-io-mirror.conf"
        echo "location = \"${mirror}\"" >> "${PODMAN_REGISTRY_DIR}/00-docker-io-mirror.conf"
        echo "insecure = false" >> "${PODMAN_REGISTRY_DIR}/00-docker-io-mirror.conf"
    done

    # 循环生成其他Registry配置
    for reg in "${REGISTRIES[@]}"; do
        IFS="|" read -r prefix mirror index <<< "$reg"
        echo "🔧 Configuring ${prefix} mirror: ${mirror}"
        generate_registry_config "${prefix}" "${mirror}" > "${PODMAN_REGISTRY_DIR}/${index}-${prefix//./-}-mirror.conf"
    done

    # 启用podman服务自启
    loginctl enable-linger $USER
    systemctl --user enable --now podman-restart.service 2>/dev/null || true

    echo "✅ Podman registry mirrors configured successfully (take effect immediately)"
fi

# ------------------------------
# 配置完成
# ------------------------------
echo ""
echo "✅ All configuration complete! All settings are user-level, no root required."
echo ""
echo "🔍 Verify configuration: podman info | grep -A 20 'registries:'"
echo ""
echo "📝 To disable all mirrors: rm -f $HOME/.config/containers/registries.conf.d/*-mirror.conf"