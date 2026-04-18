


DEST=~/.activate/headless-browser

mkdir -p "$DEST" && cd "$DEST"

npm init -y
npm install @playwright/test@1.40.0
PLAYWRIGHT_DOWNLOAD_HOST=https://registry.npmmirror.com/-/binary/playwright npx playwright install chromium --force

# npm install agent-browser
# agent-browser install  # Download Chrome from Chrome for Testing (first time only)