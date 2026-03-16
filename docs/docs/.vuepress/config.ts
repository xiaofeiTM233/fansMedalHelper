import { localTheme } from "./theme";
import { defineUserConfig } from "@vuepress/cli";
import { registerComponentsPlugin } from "@vuepress/plugin-register-components";
import { path } from "@vuepress/utils";

export default defineUserConfig({
    base: "/",
    lang: "zh-CN",
    title: "B站粉丝牌助手文档",
    description: "B站粉丝牌助手文档",
    head: [["link", { rel: "icon", href: "/images/logo.png" }]],
    theme: localTheme({
        title: "B站粉丝牌助手文档",
        description: "B站粉丝牌助手文档",
        logo: "/images/logo.png",
        navbar: [
            { text: "首页", link: "/" },
            {
                text: "指南",
                link: "/guide/",
                children: [
                    {
                        text: "项目介绍",
                        link: "/guide/",
                        activeMatch: "/guide/",
                    },
                    {
                        text: "部署方式",
                        children: [
                            {
                                text: "阿里云函数部署（0 基础）",
                                link: "/guide/ali-cloud-simple",
                            },
                            {
                                text: "阿里云函数部署",
                                link: "/guide/ali-cloud",
                            },
                            {
                                text: "腾讯云函数部署",
                                link: "/guide/tx-cloud",
                            },
                            {
                                text: "Docker 部署",
                                link: "/guide/docker",
                            },
                            {
                                text: "青龙面板部署",
                                link: "/guide/qinglong",
                            },
                            {
                                text: "本地/服务器部署",
                                link: "/guide/location",
                            },
                        ],
                    },
                ],
            },
            { text: "更新日志", link: "/changelog/" },
            {
                text: "小工具",
                link: "/tools/",
                children: [
                    {
                        text: "粉丝牌等级计算器",
                        link: "/tools/fansMedalCaculator",
                    },
                    {
                        text: "配置文件生成器",
                        link: "/tools/userConfigGenerator",
                    },
                ],
            },
        ],
        repo: "xiaofeiTM233/fansMedalHelper",
        docsRepo: "https://github.com/xiaofeiTM233/fansMedalHelperVersion",
        docsBranch: "master",
        docsDir: "docs",
        editLinkPattern: ":repo/edit/:branch/:path",
        editLink: true,
        editLinkText: "在 GitHub 上编辑此页",
        contributorsText: "文档贡献者",
    }),
    plugins: [
        registerComponentsPlugin({
            componentsDir: path.resolve(__dirname, "./components"),
        }),
    ],
});
