#!/bin/bash
# =============================================================================
# Debian/Ubuntu Aliyun Mirror Configuration Script
# Optimized for robustness, automation, and error handling.
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Constants
SOURCES_FILE="/etc/apt/sources.list"
SOURCES_D_DIR="/etc/apt/sources.list.d"
BACKUP_SUFFIX=".backup.$(date +%Y%m%d%H%M%S)"

# Logging
log_info() {  echo -e "${GREEN}[INFO]${NC}  $1"; }
log_warn() {  echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

# Dependency Check
check_env() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)."
        exit 1
    fi
}

# Get Debian Version Codename
get_codename() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$VERSION_CODENAME"
    else
        log_error "Cannot determine OS version via /etc/os-release."
        exit 1
    fi
}

main() {
    check_env
    
    local codename
    codename=$(get_codename)
    log_info "Detected Debian version: ${codename}"

    # Backup logic
    if [[ -f "$SOURCES_FILE" ]]; then
        cp "$SOURCES_FILE" "${SOURCES_FILE}${BACKUP_SUFFIX}"
        log_info "Backup created: ${SOURCES_FILE}${BACKUP_SUFFIX}"
    fi

    # Handle Debian 12+ DEB822 format (sources.list.d/debian.sources)
    local deb822_file="${SOURCES_D_DIR}/debian.sources"
    if [[ -f "$deb822_file" ]]; then
        mv "$deb822_file" "${deb822_file}${BACKUP_SUFFIX}"
        log_warn "Dispatched existing DEB822 configuration to backup."
    fi

    # Write new sources.list with dynamic codename
    log_info "Writing Aliyun mirror sources for ${codename}..."
    
    cat > "$SOURCES_FILE" <<EOF
# Debian ${codename} Aliyun Mirror
deb https://mirrors.aliyun.com/debian/ ${codename} main non-free non-free-firmware contrib
deb-src https://mirrors.aliyun.com/debian/ ${codename} main non-free non-free-firmware contrib

deb https://mirrors.aliyun.com/debian-security/ ${codename}-security main contrib non-free non-free-firmware
deb-src https://mirrors.aliyun.com/debian-security/ ${codename}-security main contrib non-free non-free-firmware

deb https://mirrors.aliyun.com/debian/ ${codename}-updates main non-free non-free-firmware contrib
deb-src https://mirrors.aliyun.com/debian/ ${codename}-updates main non-free non-free-firmware contrib

deb https://mirrors.aliyun.com/debian/ ${codename}-backports main non-free non-free-firmware contrib
deb-src https://mirrors.aliyun.com/debian/ ${codename}-backports main non-free non-free-firmware contrib
EOF

    # Finalize
    log_info "Configuration complete. Triggering package index update..."
    apt-get update -y || { log_error "Failed to update apt index."; exit 1; }
    log_info "System updated successfully."
}

main "$@"