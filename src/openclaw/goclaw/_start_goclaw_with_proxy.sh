#!/bin/bash

# 1. 杀掉旧进程，使用更准确的匹配
pkill -f "./goclaw" || true
sleep 1

DEST="$HOME/programs/goclaw"

export HTTPS_PROXY=http://127.0.0.1:7890
export HTTP_PROXY=http://127.0.0.1:7890

cd "$DEST" 
chmod +x ./goclaw
source .env.local && nohup ./goclaw > goclaw.log 2>&1 &

sleep 1
if ps aux | grep -v grep | grep "goclaw" > /dev/null; then
    echo "goclaw started successfully. PID: $!"
else
    echo "goclaw failed to start. Last 10 lines of goclaw.log:"
    tail -n 10 goclaw.log
fi