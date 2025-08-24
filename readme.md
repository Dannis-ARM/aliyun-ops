### SSH

```cmd
ssh -i "%userprofile%\.ssh\ali-ecs-key.pem" "debian@aliyun-ecs-mini.dannis-futures-ai.top"

set src_file="E:\Cloud\CloudDownloads\ddns-go_6.12.4_darwin_x86_64.tar.gz"
scp -i "%userprofile%\.ssh\ali-ecs-key.pem" %src_file% "debian@aliyun-ecs-mini.dannis-futures-ai.top:~/downloads"

```

```ps1
ssh -i "$env:USERPROFILE/.ssh/ali-ecs-key.pem" "debian@aliyun-ecs-mini.dannis-futures-ai.top"
```