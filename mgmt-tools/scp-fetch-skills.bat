scp -i "%USERPROFILE%\.ssh\aliops-key" ^
    -r aliops@ecs-mini.aliyun.gilded-age.cn:/home/aliops/.claude/skills ^
    "%USERPROFILE%\.claude\skills"