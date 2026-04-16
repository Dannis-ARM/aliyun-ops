#查询当前使用的镜像源
npm get registry

#设置为淘宝镜像源 
npm config set registry https://registry.npmmirror.com/

#验证设置
npm get registry

#还原为官方源
# npm config set registry https://registry.npmjs.org/