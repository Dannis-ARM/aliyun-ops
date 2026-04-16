git config --global url."https://gh-proxy.com/https://github.com/".insteadOf "https://github.com/"
# setup git mirror
git config --global protocol.https.allow always
# unset git mirror
# git config --global --unset url."https://gh-proxy.com/https://github.com/".insteadOf