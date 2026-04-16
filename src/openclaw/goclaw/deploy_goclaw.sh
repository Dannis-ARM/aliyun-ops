#!/bin/bash

set -euo pipefail

mkdir -p ~/programs && cd ~/programs

[[ ! -d "goclaw" ]] && git clone https://github.com/nextlevelbuilder/goclaw.git

cd goclaw

# Generate .env with auto-generated secrets
chmod +x prepare-env.sh && ./prepare-env.sh

make up



# ─────────────────────────────────────────────────────────────────────────────
# goclaw cfgs setup
# https://github.com/nextlevelbuilder/goclaw
# ─────────────────────────────────────────────────────────────────────────────