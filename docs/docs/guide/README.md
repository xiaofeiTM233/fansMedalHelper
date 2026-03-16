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

# 开始

当前版本：0.4.1（文档版本：0.3.8，没空更新文档，请参考项目根目录的示例配置文件自行配置，如有问题请参考 README 的指引反馈）

## 目前已实现功能

| 功能                       | 奖励                     |
| -------------------------- | ------------------------ |
| 每日直播区签到             | 直播区经验，银瓜子，辣条 |
| 每日点赞 1 次直播间        | 100 亲密度               |
| 每日分享 1 次直播间        | 100 亲密度               |
| 每日观看 65 分钟           | 100\*13 亲密度           |
| 每日弹幕打卡               | 点亮牌子                 |
| 每日应援团签到(如果有的话) | 10\*1 亲密度             |
| 多账号支持                 |                          |
| 微信推送通知               |                          |

<small>ps: 新版 B 站粉丝牌的亲密度每一个牌子都将单独计算 </small>

## 配置文件说明 users.yaml

```yaml
USERS:
    - access_key: XXXXXX # 注意冒号后的空格 否则会读取失败 英文冒号
      white_uid: 0 # 白名单用户ID, 可以是多个用户ID, 以逗号分隔,填写后只会打卡这些用户,黑名单失效，不用就填0
      banned_uid: 0 # 黑名单UID 同上,填了后将不会打卡，点赞，分享 用英文逗号分隔 不填则不限制,两个都填0则不限制,打卡所有直播间
    - access_key:
      white_uid: 0
      banned_uid: 0
    # 注意对齐
    # 多用户以上格式添加
    # 井号后为注释 井号前后必须有空格！井号前后必须有空格！井号前后必须有空格！
    # 冒号后面也要有空格！冒号前面也要有空格！冒号前面也要有空格！
    # 英文冒号,英文逗号！英文逗号！英文逗号！
CRON: # 0 0 * * *
# 这里是 cron 表达式, 第一个参数是分钟, 第二个参数是小时
# 例如每天凌晨0点0分执行一次为 0 0 * * *
# 如果不填,则不使用内置定时器,填写正确后要保持该进程一直运行

SENDKEY: # Server酱微信推送 可选 获取地址：https://sct.ftqq.com/
MOREPUSH: # 更多种类的推送 详细配置见文档

PROXY: # 推送代理地址,如：http://1.2.3.4:5678 支持 http/socks4/socks5 不支持 https 不用代理的不用填
#########以下为自定义配置#########

ASYNC: 1 # 异步执行,默认异步执行,设置为0则同步执行,开启异步后,将不支持设置点赞和分享CD时间

LIKE_CD: 2 # 点赞间隔时间,单位秒,默认2秒,仅为同步时生效,设置为0则不点赞

DANMAKU_CD: 6 # 弹幕间隔时间,单位秒,默认6秒,设置为0则不发弹幕打卡,只能同步打卡

WATCHINGLIVE: 65 # 每日观看直播时长，单位 min ，设置为0则关闭, 默认 65 分钟

WEARMEDAL: 0 # 是否弹幕打卡时自动带上当前房间的粉丝牌，避免房间有粉丝牌等级禁言，默认关闭，设置为1则开启

SIGNINGROUP: 2 # 应援团签到CD时间,单位秒,默认2秒,设置为0则不签到
# 说明：
# 本项目中的异步执行指的是：同时点赞或者分享所有直播间，速度非常快，但缺点就是可能会被B站吞掉亲密度，所以建议粉丝牌较少的用户开启异步执行
# 粉丝牌数大于30的用户建议使用同步，会更加稳定。缺点就是速度比较慢，但是可以设置点赞和分享的CD时间，避免被B站吞掉亲密度
# 多用户之间依然是异步，不受配置影响
```
::: tip 提示
B 站 `access_key` 获取工具：[Release B 站 access_key 获取工具 · XiaoMiku01/fansMedalHelper (github.com)](https://github.com/XiaoMiku01/fansMedalHelper/releases/tag/logintool)
:::

::: warning 警告
请务必严格填写，否则程序将读取失败，可以在这里 [YAML、YML 在线编辑器(格式化校验)-BeJSON.com](https://www.bejson.com/validators/yaml_editor/) 验证你填的 yaml 是否正确。
:::



## 多种推送方式配置 MOREPUSH 参数 （可选）

| 推送方式                                                                             | 参数                                                                                                               |
| ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| [bark](https://apps.apple.com/us/app/bark-customed-notifications/id1403753865)       | {"notifier":"bark","params":{"markdown":false,"key":"xxxxxx"}}                                                     |
| [dingtalk](https://open.dingtalk.com/document/group/custom-robot-access) 钉钉机器人  | {"notifier":"dingtalk","params":{"markdown":false,"token":"xxxxxx"}}                                               |
| [discord](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) | {"notifier":"discord","params":{"markdown":false,"webhook":"https://discord.com/api/webhooks/xxxxxx"}}             |
| [pushplus](https://www.pushplus.plus/)                                               | {"notifier":"pushplus","params":{"markdown":false,"token":"xxxxxx"}}                                               |
| [qmsg](https://qmsg.zendee.cn/)                                                      | {"notifier":"qmsg","params":{"markdown":false,"key":"xxxxxx"}}                                                     |
| [telegram](https://core.telegram.org/bots)                                           | {"notifier":"telegram","params":{"markdown":false,"token":"xxxxxx","userid":"xxxxxx"}}                             |
| [wechatworkapp](https://developer.work.weixin.qq.com/document/path/90236) 企业微信   | {"notifier":"wechatworkapp","params":{"markdown":true,"corpid":"xxxxxx","corpsecret":"xxxxxx","agentid":"xxxxxx"}} |
| [wechatworkbot ](https://developer.work.weixin.qq.com/document/path/91770) 企业微信  | {"notifier":"wechatworkbot","params":{"markdown":false,"key":"xxxxxx"}}                                            |
| [lark](https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNxkjN) 飞书       | {"notifier": "lark", "params": {"webhook": "xxxxxx", "keyword": "", "sign": ""}}                                   |

::: tip 例如

我想用 `pushplus` 推送消息，在官方申请到的 `token` 为： `abcabcacb` ，配置文件中的 `MOREPUSH` 就如下填写

```yaml
MOREPUSH: { "notifier": "pushplus", "params": { "markdown": false, "token": "abcabcacb" } }
```

`markdown` 建议都设为 false，因为可能会出现推送格式异常。

:::

## 已知问题

> 任务完成后直播间的亲密度丢失，出现只有 200 的情况

B 站亲密度结算有延迟，可能长达几个小时。实际上已经得到 1500 亲密度了。多留意。

## 赞助

![赞助](../images/sponsor.png)
