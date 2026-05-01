: ssh -i "%USERPROFILE%\.ssh\aliops-key" -L 9090:localhost:9090 "aliops@ecs-mini.aliyun.gilded-age.cn" -N
: ssh -i "%USERPROFILE%\.ssh\aliops-key" -L 18790:localhost:18790 "aliops@ecs-mini.aliyun.gilded-age.cn" -N

:: Forward Tunnel: Goclaw UI (18790) & Clash Dashboard (9090)
ssh -i "%USERPROFILE%\.ssh\aliops-key" ^
    -o ServerAliveInterval=60 ^
    -o ExitOnForwardFailure=yes ^
    -L 9090:127.0.0.1:9090 ^
    -L 18790:127.0.0.1:18790 ^
    -L 3000:127.0.0.1:3000 ^
    -N "aliops@ecs-mini.aliyun.gilded-age.cn"
