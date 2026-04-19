mkdir -p ~/.cfgs/vault-service/data
cd ~/.cfgs/vault-service

# 生成服务文件
podman generate systemd --name vault-server --files --restart-policy=always

# 移动到 user 目录并启用
mkdir -p ~/.config/systemd/user/
mv container-vault-server.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable container-vault-server.service