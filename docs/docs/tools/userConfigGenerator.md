---
sidebar: false
---

# 配置文件生成器（旧版）

<div align="center"><Generator /></div>

# 字段说明

| 字段                       | 说明                     | 例如|
| -------------------------- | ------------------------ | ----|
| Access_key (必填)            | B站账号鉴权  [获取方式](https://github.com/XiaoMiku01/fansMedalHelper/releases/tag/logintool) | e56bb4fd8fd9b249fcf86cf3a514c451 |
| 白名单        | 只进行任务的主播 `UID`  多个用英文逗号 `,` 分开           | 672346917,672353429 |
|黑名单        | 不进行任务的主播 `UID`  多个用英文逗号 `,` 分开             | 208259,208258 |
| Corn表达式           | 只在本地部署时使用内置定时器需要填写 (本项目只支持5位表达式)            |0 0 * * *|
| Server酱SENDKEY               | Server酱微信推送服务  [获取地址](https://sct.ftqq.com/)           |SCT1344T9ruheji5FHmdxUKBqGLkLxxx|
| 配置更多推送 | 更多种类的推送             | { "notifier": "pushplus", "params": { "markdown": false, "token": "abcabcacb" } |  
| PROXY | 推送代理地址(国外使用境外推送时填写,支持 http/socks4/socks5 不支持 https) | socks5://127.0.0.1:1080 |

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
