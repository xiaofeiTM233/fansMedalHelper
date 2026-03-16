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

# 青龙面板部署

- 进入面板，左侧「依赖管理」，点击「新建依赖」，选择 **python、自动拆分**，在名称处粘贴以下内容，点击确定并等待安装完成。

    ```text
    aiohttp 
    aiohttp_socks
    loguru 
    pyyaml 
    apscheduler
    ```

- 左侧「脚本管理」，点击右上角加号，选择“新建文件”，填写脚本名称 `pull_fansMedalHelper.sh`。
    ![](../images/other/image1.png)

- 输入以下内容，点击“保存”。

    ```shell
    git clone https://github.com/XiaoMiku01/fansMedalHelper.git
    cp fansMedalHelper/users.example.yaml fansMedalHelper/users.yaml
    ```

    ![](../images/other/image2.png)

- 左侧「定时任务」，然后新建任务，名称随便填，命令填 `task pull_fansMedalHelper.sh`, 定时规则随便填，因为这个任务只要执行一次，确定。
    ![](../images/other/image3.png)

- 点击右侧运行，打开日志，等待仓库拉取完成，之后**禁用或者删除这个脚本**。

- 回到脚本管理，找到 `fansMedalHelper/users.yaml` 文件，填写自己的配置，点击“保存”。
    ![](../images/other/image5.png)
    ::: tip 提示
    配置文件说明 ：[配置文件](./#配置文件说明-users-yaml)
    :::

- 保存后新建定时任务，名称随便填，命令填 `task fansMedalHelper/index.py`, 定时规则填每天执行的时间，确定。
    ![](../images/other/image6.png)

- 部署完毕，点击运行测试，查看日志是否正常。
    ::: tip 提示
    日志中可能出现乱码，是正常现象，因为是输出的日志无法显示文字颜色。
    :::

- 如何更新
    新建一个名为 `update_fansMedalHelper.sh` 的脚本，内容为：

    ```shell
    cd fansMedalHelper
    git pull
    ```

    之后创建任务执行这个脚本，命令填 `task update_fansMedalHelper.sh`。运行完成后就更新成功。
