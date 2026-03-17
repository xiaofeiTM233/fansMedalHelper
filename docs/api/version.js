/**
 * 版本信息 API
 * 对应原 Go 代码的功能
 */
export default function handler(req, res) {
  res.status(200).json({
    version: "0.4.2",
    changelog: "适配最新版B站粉丝团规则、支持多Cron表达式、OneBot推送、自定义亲密度阈值、支持3月活动签到、支持更多功能的异步操作和间隔控制、持续维护\n请在 0.4.0 以前的版本的用户，\n尽快参考新版的示例配置文件重新进行配置，\n不要在主播直播间弹幕刷屏了！\n是没有亲密度的！\n新文档站：https://fansmedalhelper.02000721.xyz 或 https://fmh.02000721.xyz",
    notice: "",
  })
}
