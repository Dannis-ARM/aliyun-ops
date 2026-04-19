:: Reverse Tunnel: Expose Local Proxy to Remote ECS
: ssh -v -i "%USERPROFILE%\.ssh\aliops-key" -R 7890:localhost:7890 -N "aliops@ecs-mini.aliyun.gilded-age.cn"
ssh -i "%USERPROFILE%\.ssh\aliops-key" ^
    -o ServerAliveInterval=60 ^
    -o ServerAliveCountMax=3 ^
    -o ExitOnForwardFailure=yes ^
    -R 7890:127.0.0.1:7890 ^
    -N "aliops@ecs-mini.aliyun.gilded-age.cn"