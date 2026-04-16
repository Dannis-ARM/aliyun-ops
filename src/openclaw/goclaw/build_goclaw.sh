#!/bin/bash
# 🔨 Build script for GoClaw with Podman support

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }

# Configuration
TARGET_HOST="${TARGET_HOST:-user@prod-server}"
REMOTE_DIR="${REMOTE_DIR:-/opt/goclaw}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
COMPOSE_POSTGRES="${COMPOSE_POSTGRES:-docker-compose.postgres.yml}"

# Build frontend
build_frontend() {
    log_info "📦 Building frontend..."
    cd ui/web && pnpm install --frozen-lockfile && pnpm build
}

# Prepare webui dist
prepare_webui() {
    log_info "📁 Preparing webui distribution..."
    rm -rf internal/webui/dist && mkdir -p internal/webui/dist
    cp -r ui/web/dist/* internal/webui/dist/
}

# Build Go binary
build_binary() {
    log_info "🔨 Building Go binary..."
    VERSION=$(git describe --tags --abbrev=0 --match "v[0-9]*" 2>/dev/null || echo "dev")
    LDFLAGS="-s -w -X github.com/nextlevelbuilder/goclaw/cmd.Version=${VERSION}"
    CGO_ENABLED=0 go build -ldflags="${LDFLAGS}" -o goclaw .
    log_info "✅ Built goclaw v${VERSION}"
}

# Deploy to remote server via SCP
deploy_remote() {
    log_info "📤 Deploying to ${TARGET_HOST}:${REMOTE_DIR}..."
    
    # Create remote directory
    ssh -o StrictHostKeyChecking=no "${TARGET_HOST}" "mkdir -p ${REMOTE_DIR}"
    
    # Transfer binary
    scp -o StrictHostKeyChecking=no ./goclaw "${TARGET_HOST}:${REMOTE_DIR}/"
    
    # Transfer compose files
    scp -o StrictHostKeyChecking=no \
        "${COMPOSE_FILE}" \
        "${COMPOSE_POSTGRES}" \
        "${TARGET_HOST}:${REMOTE_DIR}/"
    
    # Transfer deployment scripts
    scp -o StrictHostKeyChecking=no deploy_goclaw.sh "${TARGET_HOST}:${REMOTE_DIR}/"
    
    log_info "✅ Deployment files uploaded"
}

# Main
main() {
    local BUILD_ONLY=false
    local DEPLOY_ONLY=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --build-only)
                BUILD_ONLY=true
                shift
                ;;
            --deploy-only)
                DEPLOY_ONLY=true
                shift
                ;;
            --target)
                TARGET_HOST="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
    
    # Clone and setup if needed
    mkdir -p ~/programs && cd ~/programs
    if [[ ! -d "goclaw" ]]; then
        git clone https://github.com/nextlevelbuilder/goclaw.git
    fi
    cd goclaw
    
    # Setup environment
    chmod +x prepare-env.sh && ./prepare-env.sh
    
    if [[ "${DEPLOY_ONLY}" == "false" ]]; then
        # Build process
        build_frontend
        prepare_webui
        build_binary
        
        if [[ "${BUILD_ONLY}" == "true" ]]; then
            log_info "✅ Build complete (--build-only mode)"
            exit 0
        fi
    fi
    
    # Deploy
    deploy_remote
    log_info "✅ Build and deploy complete!"
}

main "$@"
