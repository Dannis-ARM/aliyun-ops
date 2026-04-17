#!/bin/bash

set -eu
DEST="$HOME/programs/goclaw"
cd "$DEST" && source .env.local && nohup ./goclaw > goclaw.log 2>&1 & 
tail -f goclaw.log