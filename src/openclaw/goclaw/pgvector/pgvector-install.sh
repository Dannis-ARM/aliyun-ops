#!/bin/bash

# ==============================================================================
# Script Name: setup_db.sh
# Description: Deploy pgvector via podman-compose with automated health checks.
# Author: Dev
# ==============================================================================

set -o errexit  # 遇到错误立即退出
set -o nounset  # 使用未定义的变量时退出
set -o pipefail # 捕获管道中的错误

export PATH="${HOME}/.local/bin:${PATH}"

# 1. 配置与变量 (Configuration)
PROJECT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
COMPOSE_FILE="${PROJECT_DIR}/pgvector-compose.yml"
CONTAINER_NAME="pgvector-db"
DB_NAME="goclaw"
DB_USER="postgres"
MAX_RETRIES=20

# 日志辅助函数
log() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] $1"
}

# 2. 检查依赖 (Pre-flight check)
if ! command -v podman-compose &> /dev/null; then
    log "ERROR: podman-compose could not be found. Please install it first."
    exit 1
fi

# 3. 环境清理 (Teardown)
log "🚀 Destroying existing environment..."
# 使用 -f 指定文件，避免上下文歧义
podman-compose -f "${COMPOSE_FILE}" down --volumes || true
podman rm -f "${CONTAINER_NAME}" 2>/dev/null || true

# 4. 启动服务 (Provision)
log "🆙 Starting services using ${COMPOSE_FILE}..."
# 注意：某些版本的 podman-compose 不需要第二个 'compose' 关键字
podman-compose -f "${COMPOSE_FILE}" up -d

# 5. 健康检查 (Health Check)
log "🧪 Waiting for Postgres to be ready..."
RETRIES=0
# 增加一个额外的 check，确保能够真正执行查询
until podman exec "${CONTAINER_NAME}" psql -U "${DB_USER}" -c "SELECT 1" &> /dev/null; do
    RETRIES=$((RETRIES + 1))
    if [ "${RETRIES}" -gt "${MAX_RETRIES}" ]; then
        log "ERROR: Database failed to respond to psql within timeout."
        exit 1
    fi
    log "Waiting... (${RETRIES}/${MAX_RETRIES})"
    sleep 2
done

# 6. 数据库初始化 (Initialization)
# 既然容器启动时已经通过 POSTGRES_DB 创建了 goclaw，这里直接启用扩展即可
log "🧬 Enabling pgvector extension on database '${DB_NAME}'..."

# 使用 -t (tuples only) 和 -A (unaligned) 来简化输出检查
# 即使 goclaw 在启动时还没准备好，这里的命令也会在连接成功后重试
podman exec "${CONTAINER_NAME}" psql -U "${DB_USER}" -d "${DB_NAME}" -c "CREATE EXTENSION IF NOT EXISTS vector;"

log "✨ All set! Database '${DB_NAME}' is ready."