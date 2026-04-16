#!/bin/bash
# 🐳 Podman Compose deployment script for GoClaw
# Supports both Docker and Podman backends

set -euo pipefail

# Configuration
COMPOSE_CMD="${COMPOSE_CMD:-podman-compose}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
COMPOSE_POSTGRES="${COMPOSE_POSTGRES:-docker-compose.postgres.yml}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Detect container runtime
detect_runtime() {
    if command -v podman &> /dev/null; then
        COMPOSE_CMD="podman-compose"
        log_info "Using Podman as container runtime"
    elif command -v docker &> /dev/null; then
        COMPOSE_CMD="docker compose"
        log_warn "Docker detected. Consider switching to Podman for rootless containers."
    else
        log_error "Neither Podman nor Docker is installed!"
        exit 1
    fi
}

# Setup
setup() {
    mkdir -p ~/programs && cd ~/programs
    
    if [[ ! -d "goclaw" ]]; then
        git clone https://github.com/nextlevelbuilder/goclaw.git
    fi
    
    cd goclaw
    
    # Generate .env with auto-generated secrets
    chmod +x prepare-env.sh && ./prepare-env.sh
}

# Deploy using podman-compose
deploy() {
    detect_runtime
    
    log_info "🚀 Starting GoClaw deployment with ${COMPOSE_CMD}..."
    
    # Stop existing containers
    ${COMPOSE_CMD} -f "${COMPOSE_FILE}" -f "${COMPOSE_POSTGRES}" down 2>/dev/null || true
    
    # Pull latest images
    log_info "📥 Pulling latest images..."
    ${COMPOSE_CMD} -f "${COMPOSE_FILE}" -f "${COMPOSE_POSTGRES}" pull || true
    
    # Build and start services
    log_info "🔨 Building and starting services..."
    ${COMPOSE_CMD} -f "${COMPOSE_FILE}" -f "${COMPOSE_POSTGRES}" up -d --build
    
    # Cleanup old images
    log_info "🧹 Cleaning up unused images..."
    podman image prune -f 2>/dev/null || true
    
    # Show status
    log_info "✅ Deployment complete!"
    ${COMPOSE_CMD} -f "${COMPOSE_FILE}" -f "${COMPOSE_POSTGRES}" ps
}

# Main
main() {
    case "${1:-deploy}" in
        setup)
            setup
            ;;
        deploy|up)
            setup
            deploy
            ;;
        down)
            detect_runtime
            ${COMPOSE_CMD} -f "${COMPOSE_FILE}" -f "${COMPOSE_POSTGRES}" down
            ;;
        logs)
            detect_runtime
            ${COMPOSE_CMD} -f "${COMPOSE_FILE}" -f "${COMPOSE_POSTGRES}" logs -f
            ;;
        ps)
            detect_runtime
            ${COMPOSE_CMD} -f "${COMPOSE_FILE}" -f "${COMPOSE_POSTGRES}" ps
            ;;
        restart)
            detect_runtime
            ${COMPOSE_CMD} -f "${COMPOSE_FILE}" -f "${COMPOSE_POSTGRES}" restart
            ;;
        *)
            echo "Usage: $0 {setup|deploy|up|down|logs|ps|restart}"
            exit 1
            ;;
    esac
}

main "$@"



# ─────────────────────────────────────────────────────────────────────────────
# goclaw cfgs setup
# https://github.com/nextlevelbuilder/goclaw
# ─────────────────────────────────────────────────────────────────────────────