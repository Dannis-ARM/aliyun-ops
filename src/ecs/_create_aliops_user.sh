#!/bin/bash
# =============================================================================
# Script: setup_aliops_user.sh
# Description: Idempotent user creation and SSH configuration for Debian 12.
# =============================================================================

set -euo pipefail

# --- Configuration ---
USERNAME="aliops"
HOME_DIR="/home/$USERNAME"
SSH_DIR="$HOME_DIR/.ssh"
AUTH_KEYS="$SSH_DIR/authorized_keys"

# --- Logging ---
log_info() { echo -e "\033[0;32m[INFO]\033[0m $(date '+%Y-%m-%d %H:%M:%S') - $1"; }
log_warn() { echo -e "\033[1;33m[WARN]\033[0m $(date '+%Y-%m-%d %H:%M:%S') - $1"; }
log_err()  { echo -e "\033[0;31m[ERROR]\033[0m $(date '+%Y-%m-%d %H:%M:%S') - $1" >&2; }

# --- Error Handling ---
trap 'log_err "Line $LINENO: Command failed with exit code $?"' ERR

# --- Validation ---
PUBLIC_KEY="${1:-}"
if [[ -z "$PUBLIC_KEY" ]]; then
    log_err "Missing argument: SSH public key is required."
    exit 1
fi

# --- Execution ---

# 1. User Creation
if id "$USERNAME" &>/dev/null; then
    log_warn "User '$USERNAME' already exists. Skipping creation."
else
    log_info "Creating user '$USERNAME'..."
    useradd -m -s /bin/bash "$USERNAME" || { log_err "Failed to create user"; exit 1; }
fi

# 2. Directory Setup
if [[ ! -d "$SSH_DIR" ]]; then
    log_info "Creating SSH directory: $SSH_DIR"
    mkdir -p "$SSH_DIR"
    chmod 700 "$SSH_DIR"
else
    log_info "SSH directory already exists."
fi

# 3. Key Configuration (Idempotent)
if [[ -f "$AUTH_KEYS" ]] && grep -Fq "$PUBLIC_KEY" "$AUTH_KEYS"; then
    log_warn "Public key already exists in authorized_keys. Skipping."
else
    log_info "Adding public key to $AUTH_KEYS"
    # Ensure newline before appending to prevent corruption if file ended abruptly
    [[ -f "$AUTH_KEYS" ]] && sed -i '$a\' "$AUTH_KEYS"
    echo "$PUBLIC_KEY" >> "$AUTH_KEYS"
    chmod 600 "$AUTH_KEYS"
fi

# 4. Final Permissions Check
log_info "Applying ownership: $USERNAME:$USERNAME"
chown -R "$USERNAME:$USERNAME" "$SSH_DIR"

log_info "Setup for '$USERNAME' completed successfully."