### SSH

```cmd
: ssh
ssh -i "%userprofile%\.ssh\ali-ecs-key.pem" "debian@aliyun-ecs-mini.dannis-futures-ai.top"

: scp ddns-go
set src_file="E:\Cloud\CloudDownloads\ddns-go_6.12.4_linux_x86_64.tar.gz"
scp -i "%userprofile%\.ssh\ali-ecs-key.pem" %src_file% "debian@aliyun-ecs-mini.dannis-futures-ai.top:~/downloads/ddns-go"

: scp ddns-go cfg
set src_file="E:\Projects\PythonProjects\aliyun-ops\.ddns_go_config.yaml"
scp -i "%userprofile%\.ssh\ali-ecs-key.pem" %src_file% "debian@aliyun-ecs-mini.dannis-futures-ai.top:~/.cfgs/.ddns_go_config.yaml"
```

```ps1
ssh -i "$env:USERPROFILE/.ssh/ali-ecs-key.pem" "debian@aliyun-ecs-mini.dannis-futures-ai.top"
```