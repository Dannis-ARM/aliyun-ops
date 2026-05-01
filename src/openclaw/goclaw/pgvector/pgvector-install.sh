#!/bin/bash

# 配置严格模式
set -euo pipefail

# 1. 环境初始化：解决命令找不到与路径偏差
export PATH="${HOME}/.local/bin:/usr/local/bin:/usr/bin:/bin:${PATH}"
PROJECT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)

# 2. 变量定义 (带默认值保护)
CONTAINER_NAME="pgvector-db"
DB_NAME="${DB_NAME:-goclaw}"
DB_USER="${DB_USER:-postgres}"
MAX_RETRIES=${MAX_RETRIES:-20}
COMPOSE_FILE="${PROJECT_DIR}/pgvector-compose.yml"

# 日志美化
log()   { printf "\033[0;32m[$(date +'%T')] INFO: %b\033[0m\n" "$1"; }
error() { printf "\033[0;31m[$(date +'%T')] ERROR: %b\033[0m\n" "$1" >&2; }

# 3. 预检
[[ ! -f "${COMPOSE_FILE}" ]] && { error "找不到文件: ${COMPOSE_FILE}"; exit 1; }
command -v podman-compose &>/dev/null || { error "未安装 podman-compose"; exit 1; }

# 4. 启动与更新
log "🚀 正在同步容器状态..."
podman-compose -f "${COMPOSE_FILE}" up -d

# 5. 健康检查 (使用 pg_isready)
log "🧪 等待数据库就绪..."
for i in $(seq 1 "${MAX_RETRIES}"); do
    if podman exec "${CONTAINER_NAME}" pg_isready -U "${DB_USER}" -d "${DB_NAME}" &>/dev/null; then
        log "✅ 数据库已就绪"
        break
    fi
    [[ "$i" -eq "${MAX_RETRIES}" ]] && { error "等待超时"; exit 1; }
    sleep 2
done

# 6. 初始化扩展
log "🧬 启用 pgvector 扩展..."
podman exec "${CONTAINER_NAME}" psql -U "${DB_USER}" -d "${DB_NAME}" \
    -c "CREATE EXTENSION IF NOT EXISTS vector;" &>/dev/null

log "✨ 部署成功！"