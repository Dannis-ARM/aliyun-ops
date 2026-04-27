


DEST=~/.activate/headless-browser

mkdir -p "$DEST" && cd "$DEST"

npm init -y
npm install @playwright/test@1.40.0 # newer version e.g. 1.59.1 hasn't been updated in CN Cache
PLAYWRIGHT_DOWNLOAD_HOST=https://registry.npmmirror.com/-/binary/playwright npx playwright install chromium --force
ls -al ~/.cache/ms-playwright

# Alternative SCP / using agent-browser to get chromium
# npm install agent-browser
# agent-browser install  # Download Chrome from Chrome for Testing (first time only)

# setup aws cli - https://github.com/microsoft/playwright-cli
npm install -g @playwright/cli@latest
playwright-cli --help