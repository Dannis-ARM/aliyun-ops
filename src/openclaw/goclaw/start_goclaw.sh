#!/bin/bash

pkill -f "/./goclaw" || true
sleep 0.5

# export HTTPS_PROXY=http://127.0.0.1:7890
# export HTTP_PROXY=http://127.0.0.1:7890

DEST="$HOME/programs/goclaw"
cd "$DEST" && source .env.local && nohup ./goclaw > goclaw.log 2>&1 &

# sleep 1
# tail -f goclaw.log