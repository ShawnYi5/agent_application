# 项目说明
本项目展现使用 Glacier2 组件进行数据穿透转发的实例

# 模块说明
### agent_python
运行在远端的agent
功能为：
* 与一体机创建“永久”链接
* 接收一体机的命令，连接到穿透网关
* 通过穿透网关调用到网关后的服务（也就是可调用到kvm模块）
* 接收来自穿透网关后的服务的命令（也就是可接收kvm模块的请求命令）

### kvm
运行在kvm中的agent
功能为：
* 提供通用接口
* 可注册来自穿透网关的回调（与普通回调一致）

### config.glacier2
穿透网关配置文件

### fake_BoxService
伪装的BoxService组件

# 如何开始
* 修改 config.glacier2
    * `Glacier2.Client.Endpoints=ssl -p 4064 -h 172.16.6.81` 修改为穿透网关的监听参数
    * `Glacier2.Server.Endpoints=tcp -h 172.16.6.81` 修改为穿透网关转发连接时使用的地址，例如：`Glacier2.Server.Endpoints=tcp -h 172.29.16.2`
* 修改 config.agent
    * 修改为运行 fake_BoxService 或 一体机的IP
* 修改 config.remote
    * `Ice.Default.Router=ClwGlacier/router:ssl -p 4064 -h 172.16.6.81` 修改为连接到穿透网关的端口与地址 
    * 如果需要 SSL，注意修改证书路径
* 启动 glacier2
一体机中
`glacier2router --Ice.Config=config.glacier2`
* 启动 kvm 模块
开发主机
`python agent_in_kvm.py`
* 启动 fake_BoxService模块
开发主机
`python fake_BoxService.py`
* 启动 agent_python模块
开发主机
`python agent_in_remote.py`