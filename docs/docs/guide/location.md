---
sidebar:
    - /guide/
    - /guide/ali-cloud-simple/
    - /guide/ali-cloud/
    - /guide/tx-cloud/
    - /guide/docker/
    - /guide/qinglong/
    - /guide/location/
---

# 本地/服务器部署

::: warning 注意
环境需求：Python 版本大于 3.8
:::

## 克隆项目并安装依赖

```shell
git clone https://github.com/XiaoMiku01/fansMedalHelper.git
cd fansMedalHelper
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 填写配置文件 users.yaml

复制 `users.example.yaml` 并命名为 `users.yaml`，并填写 `users.yaml`。Windows 使用记事本方式打开，Linux 使用用 vim。

```shell
cp users.example.yaml users.yaml
vim users.yaml
```

配置文件说明：[配置文件](./#配置文件说明-users-yaml)

## 运行主程序

### 单次运行

```shell
python main.py
```

默认只运行一次，需要结合**任务计划程序（Windows）** 或 **crontab （Linux / macOS）** 实现每日定时调用。

### 自动调度

若附加 `--auto` 参数运行，即：

```shell
python main.py --auto
```

将进入自动调度模式，每 24 小时自动运行一次，需要结合进程守护工具使用，如：

- [PM2](https://pm2.io/)：基于 Node.js 的守护进程和管理工具
- [Forever](https://github.com/foreversd/forever)：基于 Node.js 的守护进程和管理工具
- [systemd](https://systemd.io/)：Linux 系统服务管理器
- [Supervisor](http://supervisord.org/)：进程守护工具

## 效果图

![](../images/location/img1.png)

## 更新方式

进入项目文件夹后，执行 `git pull` 更新代码。

```shell
git pull
```
