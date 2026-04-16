#!/bin/bash
# https://github.com/nelvko/clash-for-linux-install?tab=readme-ov-file

set -euo pipefail

mkdir -p ~/.activate
cd ~/.activate

clashInstallScript="https://gh-proxy.org/https://github.com/nelvko/clash-for-linux-install.git"

git clone --branch master --depth 1 ${clashInstallScript} \
  && cd clash-for-linux-install \
  && bash install.sh
