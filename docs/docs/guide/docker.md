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

# Docker 部署

:::tip 提示
如果**访问 DockerHub 不通畅**或**宿主机为 arm 架构**，可使用支持多架构的国内镜像 `registry.cn-shanghai.aliyuncs.com/xm798/fansmedalhelper:latest` 替换 `xiaomiku01/fansmedalhelper:latest`。
:::

## 配置用户信息并运行

:::tip 提示
若填写 CRON 表达式，则按照指定时间运行；

若不填写，则按照容器启动时间，每 24 小时运行一次。
:::

### 使用配置文件

1. 下载 [配置文件](https://github.com/XiaoMiku01/fansMedalHelper/blob/master/users.example.yaml) 并重命名为 `users.yaml`，依据 [配置文件说明](./#配置文件说明-users-yaml) 填写各项内容，并记录下配置文件的绝对路径。

2. 运行容器，其中 `/path-to-your-config/users.yaml` 替换为 **配置文件的本地绝对路径**。

    ```shell
    docker run -d \
    -v /path-to-your-config/users.yaml:/app/fansMedalHelper/users.yaml \
    --name fansmedalhelper \
    xiaomiku01/fansmedalhelper:latest
    ```

### 使用环境变量

1. 复制填写好的配置文件，使用 [yaml-to-json](https://www.convertjson.com/yaml-to-json.htm) 将 yaml 格式文件转换成 json 格式。

    ::: warning 注意
    需勾选右边的 `Minimize JSON` 以压缩 JSON
    :::

    ![yaml-to-json](../images/other/image7.png)

2. 运行容器

    ```shell
    docker run -d \
    -e USERS='<这里填写刚刚转换的 json 格式字符串>' \
    --restart unless-stopped \
    --name fansmedalhelper \
    xiaomiku01/fansmedalhelper:latest
    ```

    ::: warning 警告
    json 字符串必须用单引号括起来，否则无法识别。
    :::
    例如：

    ```shell
    docker run -d \
    -e USERS='{"users": [{"user_id": "123456789", "access_key": "123456789", "secret_key": "123456789"}]}' \
    --restart unless-stopped \
    --name fansmedalhelper \
    xiaomiku01/fansmedalhelper:latest
    ```

## Compose 部署容器

1. 新建一个工作目录，根据上面 [使用配置文件](#使用配置文件) 部分，下载并填写配置文件，命名为 `users.yaml` 放置于目录中。

2. 继续在该目录中，创建 `docker-compose.yaml` 配置文件：

    ```yaml
    version: '3.3'
    services:
      fansmedalhelper:
        container_name: fansmedalhelper
        image: xiaomiku01/fansmedalhelper:latest
        volumes:
          - ./users.yaml:/app/fansMedalHelper/users.yaml
        environment:
          - MIRRORS=1 # 使用镜像
        restart: unless-stopped
    ```

3. 启动容器：

    ```bash
    docker compose up -d
    # 或 docker-compose up -d
    ```

## 查看日志

```shell
docker logs -f fansmedalhelper
# 结束按 Ctrl-C
```

## 更新方式

:::tip 提示
每次容器启动后都会自动拉取最新代码，所有只需要重启容器即可。
:::

```shell
docker restart fansmedalhelper
```

## 使用仓库镜像

:::tip 提示
如果大陆地区访问 GitHub 不通畅导致更新失败，可以配置仓库镜像。
:::

在运行 docker 命令行时添加如下环境变量：

- `-e MIRRORS=1` 使用 [GHProxy](https://ghproxy.com/)
- `-e MIRRORS=2` 使用 [FastGIT](http://fastgit.org/)
- `-e MIRRORS=custom -e CUSTOM_REPO=https://gitee.com/user/repo` 使用自定义镜像

例如：

  ```shell
  docker run -d \
  -v /path-to-your-config/users.yaml:/app/fansMedalHelper/users.yaml \
  -e MIRRORS=1 \
  --name fansmedalhelper \
  xiaomiku01/fansmedalhelper:latest
  ```
