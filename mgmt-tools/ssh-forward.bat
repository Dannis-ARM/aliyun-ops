: ssh -i "%USERPROFILE%\.ssh\aliops-key" -L 9090:localhost:9090 "aliops@ecs-mini.aliyun.gilded-age.cn" -N
: ssh -i "%USERPROFILE%\.ssh\aliops-key" -L 18790:localhost:18790 "aliops@ecs-mini.aliyun.gilded-age.cn" -N

ssh -i "%USERPROFILE%\.ssh\aliops-key" ^
    -L 9090:localhost:9090 ^
    -L 18790:localhost:18790 ^
    -N "aliops@ecs-mini.aliyun.gilded-age.cn"

