# Dannis's Personal Aliyun VM

个人阿里云 ECS 实例管理仓库。

## 快速链接

- [Aliyun ECS Console](https://ecs.console.aliyun.com/home)

## 目录

- [Dannis's Personal Aliyun VM](#danniss-personal-aliyun-vm)
  - [快速链接](#快速链接)
  - [目录](#目录)
  - [Git 配置](#git-配置)
  - [SSH 连接](#ssh-连接)
    - [Windows CMD](#windows-cmd)
    - [Windows PowerShell](#windows-powershell)
  - [DDNS-GO 部署](#ddns-go-部署)
    - [部署步骤](#部署步骤)
      - [上传程序和配置文件](#上传程序和配置文件)
    - [访问 DDNS-GO Web UI](#访问-ddns-go-web-ui)
    - [UV setup](#uv-setup)
    - [clash local port forwarding](#clash-local-port-forwarding)
    - [goclaw](#goclaw)
- [May consider this](#may-consider-this)
- [hetzner vps](#hetzner-vps)

---

## Git 配置

```bash
# 移除旧的远程仓库
git remote remove origin

# 添加新的远程仓库
git remote add origin git@github.com:Dannis-ARM/aliyun-ops.git
```

---

## SSH 连接

> ECS 实例域名: `ecs-mini.aliyun.gilded-age.cn`  
> 用户名: `debian`  
> 密钥文件: `~/.ssh/ali-ecs-key.pem`

### Windows CMD

Admin  
`ssh -i "%USERPROFILE%\.ssh\ali-ecs-key.pem" "debian@ecs-mini.aliyun.gilded-age.cn"`  
Normal User  
`ssh -i "%USERPROFILE%\.ssh\aliops-key" "aliops@ecs-mini.aliyun.gilded-age.cn"`

### Windows PowerShell

`ssh -i "$env:USERPROFILE/.ssh/ali-ecs-key.pem" "debian@ecs-mini.aliyun.gilded-age.cn"`

---

## DDNS-GO 部署

[DDNS-GO](https://github.com/jeessy2/ddns-go) 动态域名客户端，用于自动更新 DNS 记录。

### 部署步骤

#### 上传程序和配置文件

```cmd
:: Windows CMD
scp -i "%USERPROFILE%\.ssh\ali-ecs-key.pem" "E:\Cloud\CloudDownloads\ddns-go_6.12.4_linux_x86_64.tar.gz" "debian@ecs-mini.aliyun.gilded-age.cn:~/downloads/ddns-go"

scp -i "%USERPROFILE%\.ssh\ali-ecs-key.pem" "E:\Projects\PythonProjects\aliyun-ops\.ddns_go_config.yaml" "debian@ecs-mini.aliyun.gilded-age.cn:~/.cfgs/.ddns_go_config.yaml"
```

### 访问 DDNS-GO Web UI

浏览器访问: http://ecs-mini.aliyun.gilded-age.cn:9876/login


### UV setup
```batch
uv init
uv add requests

# After adding 
[tool.uv]
package = true

# D:\MyProjects\zyuyan\aliyun-ops\src\openclaw\activate.py
uv run D:\MyProjects\zyuyan\aliyun-ops\src\openclaw\activate.py
```

### clash local port forwarding
```
$ clashui
╔═══════════════════════════════════════════════╗
║                😼 Web 控制台                   ║
║═══════════════════════════════════════════════║
║                                               ║
║     🔓 注意放行端口：9090                       ║
║     🏠 内网：http://192.168.0.1:9090/ui        ║
║     🌏 公网：http://8.8.8.8:9090/ui            ║
║     ☁️ 公共：http://board.zash.run.place       ║
║                                               ║
╚═══════════════════════════════════════════════╝

$ clashsecret mysecret
😼 密钥更新成功，已重启生效

$ clashsecret
😼 当前密钥：mysecret

ssh -i "%USERPROFILE%\.ssh\aliops-key" -L 9090:localhost:9090 "aliops@ecs-mini.aliyun.gilded-age.cn" -N
```

### goclaw
[GIthub](https://github.com/nextlevelbuilder/goclaw)
[mgmt-tool](E:\Projects\PythonProjects\aliyun-ops\mgmt-tools\ssh-forward.bat)
```
# Web Dashboard at http://localhost:18790 (built-in)
# Health check: curl http://localhost:18790/health

: ssh -i "%USERPROFILE%\.ssh\aliops-key" -L 18790:localhost:18790 "aliops@ecs-mini.aliyun.gilded-age.cn" -N
source .env.local && ./goclaw
```

# May consider this 
# hetzner vps


`cat ~/test | sudo tee -a /home/aliops/.ssh/authorized_keys > /dev/null`