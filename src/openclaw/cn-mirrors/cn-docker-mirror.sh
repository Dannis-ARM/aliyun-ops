#!/bin/bash

set -euo pipefail

mkdir -p ~/.config/containers

cat > ~/.config/containers/registries.conf << 'EOF'
unqualified-search-registries = ["docker.io"]

[[registry]]
prefix = "docker.io"
location = "docker.io"

[[registry.mirror]]
location = "6l8h60n8.mirror.aliyuncs.com"
[[registry.mirror]]
location = "docker.m.daocloud.io"
[[registry.mirror]]
location = "dockerproxy.com"
[[registry.mirror]]
location = "mirror.baidubce.com"

EOF
