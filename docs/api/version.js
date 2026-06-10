/**
 * 版本信息 API
 * 对应原 Go 代码的功能
 */
export default function handler(req, res) {
  res.status(200).json({
    version: "0.4.4",
    changelog: "修复原作者改坏的点赞接口\n请在 0.4.0 以前的版本的用户，\n尽快参考新版的示例配置文件重新进行配置\n新文档站：https://fansmedalhelper.02000721.xyz 或 https://fmh.02000721.xyz",
    notice: "",
  })
}
