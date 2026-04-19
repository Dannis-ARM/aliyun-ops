#!/bin/bash

# ─────────────────────────────────────────────────────────────────────────────
# goclaw cfgs setup - Minimalist Version
# ─────────────────────────────────────────────────────────────────────────────

set -eu

SRC="$HOME/.activate/goclaw.tar.gz"
DEST="$HOME/programs/goclaw"

# 1. Ensure directory exists
mkdir -p "$DEST"

# 2. Extract directly to destination
if [[ -f "$SRC" ]]; then
    tar -xzf "$SRC" -C "$DEST"
    echo "[$(date)] Success: Extracted to $DEST"
else
    echo "[$(date)] Error: $SRC not found" >&2
    exit 1
fi

cd $DEST && /bin/bash $DEST/_start_goclaw.sh