from aiohttp import ClientSession, ClientTimeout
import sys
import os
import asyncio
import uuid
import time
from loguru import logger
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> <blue> {extra[user]} </blue> <level>{message}</level>",
    backtrace=True,
    diagnose=True,
)


class BiliUser:
    def __init__(self, access_token: str, whiteUIDs: str = '', bannedUIDs: str = '', config: dict = {}):
        from .api import BiliApi

        self.mid, self.name = 0, ""
        self.access_key = access_token  # 登录凭证
        try:
            self.whiteList = list(map(lambda x: int(x if x else 0), str(whiteUIDs).split(',')))  # 白名单UID
            self.bannedList = list(map(lambda x: int(x if x else 0), str(bannedUIDs).split(',')))  # 黑名单
        except ValueError:
            raise ValueError("白名单或黑名单格式错误")
        self.config = config
        self.medals = []  # 用户所有勋章
        self.medalsNeedDo = []  # 用户所有勋章，需要执行任务的

        self.session = ClientSession(timeout=ClientTimeout(total=3), trust_env = True)
        self.api = BiliApi(self, self.session)

        self.retryTimes = 0  # 点赞任务重试次数
        self.maxRetryTimes = 10  # 最大重试次数
        self.message = []
        self.errmsg = ["错误日志："]
        self.uuids = [str(uuid.uuid4()) for _ in range(2)]
        self.cron_index = self.config.get("CURRENT_CRON_INDEX", 0)
        self.total_cron_count = self.config.get("TOTAL_CRON_COUNT", 0)
        self.target_cron_index = self.config.get("CRON_INDEX", 0)

    def should_execute_task(self) -> bool:
        """
        检查是否应该在当前 cron 执行任务
        返回 True 表示应该执行，False 表示跳过
        """
        if self.target_cron_index == 0:
            # 设置为 0，所有 cron 都执行
            return True
        elif self.target_cron_index > 0:
            # 设置为正整数，只在对应位置的 cron 执行
            return self.target_cron_index == self.cron_index
        elif self.target_cron_index < 0:
            # 设置为负数，表示倒数第几个
            # 例如：-1 表示倒数第 1 个（最后一个），-2 表示倒数第 2 个
            target_position = self.total_cron_count + self.target_cron_index + 1
            return target_position == self.cron_index
        return False

    def get_target_description(self) -> str:
        """
        获取目标索引的描述文本
        """
        if self.target_cron_index == 0:
            return "所有"
        elif self.target_cron_index > 0:
            return f"第{self.target_cron_index}个"
        else:
            # 负数表示倒数第几个
            return f"倒数第{abs(self.target_cron_index)}个"

    async def loginVerify(self) -> bool:
        """
        登录验证
        """
        loginInfo = await self.api.loginVerift()
        self.mid, self.name = loginInfo['mid'], loginInfo['name']
        self.log = logger.bind(user=self.name)
        if loginInfo['mid'] == 0:
            self.isLogin = False
            return False
        userInfo = await self.api.getUserInfo()
        if userInfo['medal']:
            medalInfo = await self.api.getMedalsInfoByUid(userInfo['medal']['target_id'])
            if medalInfo['has_fans_medal']:
                self.initialMedal = medalInfo['my_fans_medal']
        self.log.log("SUCCESS", str(loginInfo['mid']) + " 登录成功")
        self.isLogin = True
        return True

    async def doSign(self):
        try:
            signInfo = await self.api.doSign()
            self.log.log("SUCCESS", "签到成功,本月签到次数: {}/{}".format(signInfo['hadSignDays'], signInfo['allDays']))
            self.message.append(f"【{self.name}】 签到成功,本月签到次数: {signInfo['hadSignDays']}/{signInfo['allDays']}")
        except Exception as e:
            self.log.log("ERROR", e)
            self.errmsg.append(f"【{self.name}】" + str(e))
        userInfo = await self.api.getUserInfo()
        self.log.log(
            "INFO", "当前用户UL等级: {} ,还差 {} 经验升级".format(userInfo['exp']['user_level'], userInfo['exp']['unext'])
        )
        self.message.append(
            f"【{self.name}】 UL等级: {userInfo['exp']['user_level']} ,还差 {userInfo['exp']['unext']} 经验升级"
        )

    async def getMedals(self):
        """
        获取用户勋章
        """
        self.medals.clear()
        self.medalsNeedDo.clear()
        async for medal in self.api.getFansMedalandRoomID():
            if self.whiteList == [0]:
                if medal['medal']['target_id'] in self.bannedList:
                    self.log.warning(f"{medal['anchor_info']['nick_name']} 在黑名单中，已过滤")
                    continue
                self.medals.append(medal) if medal['room_info']['room_id'] != 0 else ...
            else:
                if medal['medal']['target_id'] in self.whiteList:
                    self.medals.append(medal) if medal['room_info']['room_id'] != 0 else ...
                    self.log.success(f"{medal['anchor_info']['nick_name']} 在白名单中，加入任务")
        min_intimacy = self.config.get("MIN_INTIMACY_THRESHOLD", 30)
        [
            self.medalsNeedDo.append(medal)
            for medal in self.medals
            if medal['medal']['level'] < 120 and medal['medal']['today_feed'] < min_intimacy
        ]
        self.log.info(f"当前亲密度阈值设置为 {min_intimacy}，未达到此阈值的牌子将执行任务")

    async def like_v3(self, failedMedals: list = []):
        if self.config['LIKE_CD'] == -1:
            self.log.log("INFO", "点赞任务已关闭")
            return
        try:
            if not failedMedals:
                failedMedals = self.medals
            if self.config['LIKE_CD'] == 0:
                # 异步点赞：CD=0，所有直播间同时点赞，不等待
                self.log.log("INFO", "异步点赞任务开始....")
                for i in range(35):
                    allTasks = []
                    for medal in failedMedals:
                        allTasks.append(self.api.likeInteractV3(medal['room_info']['room_id'], medal['medal']['target_id'], self.mid))
                    await asyncio.gather(*allTasks)
                    self.log.log("SUCCESS", f"异步点赞{i+1}次成功")
                    await asyncio.sleep(self.config['LIKE_CD'])
            else:
                # 同步点赞：CD>0，逐个直播间点赞，间隔时间为CD值
                self.log.log("INFO", f"同步点赞任务开始，间隔{self.config['LIKE_CD']}秒")
                for index, medal in enumerate(failedMedals):
                    for i in range(30):
                        tasks = []
                        tasks.append(self.api.likeInteractV3(medal['room_info']['room_id'], medal['medal']['target_id'], self.mid))
                        await asyncio.gather(*tasks)
                        await asyncio.sleep(self.config['LIKE_CD'])
                    self.log.log("SUCCESS", f"{medal['anchor_info']['nick_name']} 点赞{i+1}次成功 {index+1}/{len(self.medals)}")
            await asyncio.sleep(10)
            self.log.log("SUCCESS", "点赞任务完成")
            # finallyMedals = [medal for medal in self.medalsNeedDo if medal['medal']['today_feed'] >= 100]
            # msg = "20级以下牌子共 {} 个,完成点赞任务 {} 个".format(len(self.medalsNeedDo), len(finallyMedals))
            # self.log.log("INFO", msg)
        except Exception:
            self.log.exception("点赞任务异常")
            self.errmsg.append(f"【{self.name}】 点赞任务异常,请检查日志")

    async def sendDanmaku(self):
        """
        每日弹幕打卡
        """
        if self.config['DANMAKU_CD'] == -1:
            self.log.log("INFO", "弹幕任务已关闭")
            return
        self.log.log("INFO", "弹幕打卡任务开始....(预计 {} 秒完成)".format(len(self.medals) * max(self.config['DANMAKU_CD'], 1)))
        n = 0
        successnum = 0
        for medal in self.medals:
            n += 1
            (await self.api.wearMedal(medal['medal']['medal_id'])) if self.config['WEARMEDAL'] else ...
            try:
                danmaku = await self.api.sendDanmaku(medal['room_info']['room_id'])
                successnum+=1
                self.log.log(
                    "DEBUG",
                    "{} 房间弹幕打卡成功: {} ({}/{})".format(
                        medal['anchor_info']['nick_name'], danmaku, n, len(self.medals)
                    ),
                )
            except Exception as e:
                self.log.log("ERROR", "{} 房间弹幕打卡失败: {}".format(medal['anchor_info']['nick_name'], e))
                self.errmsg.append(f"【{self.name}】 {medal['anchor_info']['nick_name']} 房间弹幕打卡失败: {str(e)}")
            finally:
                await asyncio.sleep(self.config['DANMAKU_CD'] if self.config['DANMAKU_CD'] > 0 else 0)

        if hasattr(self, 'initialMedal'):
            (await self.api.wearMedal(self.initialMedal['medal_id'])) if self.config['WEARMEDAL'] else ...
        self.log.log("SUCCESS", "弹幕打卡任务完成")
        self.message.append(f"【{self.name}】 弹幕打卡任务完成 {successnum}/{len(self.medals)}")

    async def init(self):
        if not await self.loginVerify():
            self.log.log("ERROR", "登录失败 可能是 access_key 过期 , 请重新获取")
            self.errmsg.append("登录失败 可能是 access_key 过期 , 请重新获取")
            await self.session.close()
        else:
            await self.doSign()
            await self.getMedals()

    async def start(self):
        if self.isLogin:
            tasks = []
            should_execute = self.should_execute_task()
            min_intimacy = self.config.get("MIN_INTIMACY_THRESHOLD", 30)

            if self.medalsNeedDo:
                self.log.log("INFO", f"共有 {len(self.medalsNeedDo)} 个牌子未满 {min_intimacy} 亲密度")
                if should_execute:
                    tasks.append(self.like_v3())
                else:
                    self.log.log("INFO", f"点赞任务跳过（当前 cron 索引: {self.cron_index}/{self.total_cron_count}, 仅在{self.get_target_description()} cron 执行）")
                tasks.append(self.watchinglive())
            else:
                self.log.log("INFO", f"所有牌子已满 {min_intimacy} 亲密度")

            if should_execute:
                tasks.append(self.sendDanmaku())
                tasks.append(self.signInGroups())
                tasks.append(self.doCustomSignIn())
            else:
                self.log.log("INFO", f"弹幕签到、应援团签到、活动签到任务跳过（当前 cron 索引: {self.cron_index}/{self.total_cron_count}, 仅在{self.get_target_description()} cron 执行）")

            await asyncio.gather(*tasks)

    async def sendmsg(self):
        if not self.isLogin:
            await self.session.close()
            return self.message + self.errmsg
        await self.getMedals()
        nameList1, nameList2, nameList3, nameList4 = [], [], [], []
        for medal in self.medals:
            if medal['medal']['level'] >= 120:
                continue
            today_feed = medal['medal']['today_feed']
            nick_name = medal['anchor_info']['nick_name']
            if today_feed >= 30:
                nameList1.append(nick_name)
            elif 20 <= today_feed < 30:
                nameList2.append(nick_name)
            elif 10 <= today_feed < 20:
                nameList3.append(nick_name)
            elif today_feed < 10:
                nameList4.append(nick_name)
        self.message.append(f"【{self.name}】 今日亲密度获取情况如下：")

        for medal_list, title in zip(
            [nameList1, nameList2, nameList3, nameList4],
            ["【30】", "【20至30】", "【10至20】", "【10以下】"],
        ):
            if len(medal_list) > 0:
                self.message.append(f"{title}" + ' '.join(medal_list[:5]) + f"{'等' if len(medal_list) > 5 else ''}" + f' {len(medal_list)}个')

        if hasattr(self, 'initialMedal'):
            initialMedalInfo = await self.api.getMedalsInfoByUid(self.initialMedal['target_id'])
            if initialMedalInfo['has_fans_medal']:
                initialMedal = initialMedalInfo['my_fans_medal']
                self.message.append(
                    f"【当前佩戴】「{initialMedal['medal_name']}」({initialMedal['target_name']}) {initialMedal['level']} 级 "
                )
                if initialMedal['level'] < 120 and initialMedal['today_feed'] != 0:
                    need = initialMedal['next_intimacy'] - initialMedal['intimacy']
                    need_days = need // 30 + 1
                    end_date = datetime.now() + timedelta(days=need_days)
                    self.message.append(f"今日已获取亲密度 {initialMedal['today_feed']} (B站结算有延迟，请耐心等待)")
                    self.message.append(
                        f"距离下一级还需 {need} 亲密度 预计需要 {need_days} 天 ({end_date.strftime('%Y-%m-%d')},以每日 30 亲密度计算)"
                    )
        await self.session.close()
        return self.message + self.errmsg + ['---']

    async def watchinglive(self):
        if not self.config['WATCHINGLIVE']:
            self.log.log("INFO", "每日观看直播任务关闭")
            return
        HEART_MAX = self.config['WATCHINGLIVE']
        CD_TIME = self.config['WATCHINGLIVE_CD'] if self.config['WATCHINGLIVE_CD'] != -1 else 60
        
        self.log.log("INFO", f"每日{HEART_MAX}分钟任务开始（每个心跳包间隔{CD_TIME}秒）")
        
        if CD_TIME == 0:
            # 异步模式：所有直播间同时发送心跳包
            self.log.log("INFO", f"异步观看直播模式，共{len(self.medalsNeedDo)}个直播间")
            for heartNum in range(1, HEART_MAX+1):
                if self.config['STOPWATCHINGTIME']:
                    if int(time.time()) >= self.config['STOPWATCHINGTIME']:
                        self.log.log("INFO", "已到设置的时间，自动停止直播任务")
                        return
                
                allTasks = []
                for medal in self.medalsNeedDo:
                    allTasks.append(self.api.heartbeat(medal['room_info']['room_id'], medal['medal']['target_id']))
                
                await asyncio.gather(*allTasks)
                
                if heartNum%5==0:
                    self.log.log(
                        "INFO",
                        f"所有直播间第{heartNum}次心跳包已发送（共{len(self.medalsNeedDo)}个直播间）",
                    )
                await asyncio.sleep(CD_TIME)
        else:
            # 同步模式：逐个直播间发送心跳包
            self.log.log("INFO", f"同步观看直播模式，间隔{CD_TIME}秒，共{len(self.medalsNeedDo)}个直播间")
            n = 0
            for medal in self.medalsNeedDo:
                n += 1
                for heartNum in range(1, HEART_MAX+1):
                    if self.config['STOPWATCHINGTIME']:
                        if int(time.time()) >= self.config['STOPWATCHINGTIME']:
                            self.log.log("INFO", "已到设置的时间，自动停止直播任务")
                            return
                    tasks = []
                    tasks.append(self.api.heartbeat(medal['room_info']['room_id'], medal['medal']['target_id']))
                    await asyncio.gather(*tasks)
                    if heartNum%5==0:
                        self.log.log(
                            "INFO",
                            f"{medal['anchor_info']['nick_name']} 第{heartNum}次心跳包已发送（{n}/{len(self.medalsNeedDo)}）",
                        )
                    await asyncio.sleep(CD_TIME)
        self.log.log("SUCCESS", f"每日{HEART_MAX}分钟任务完成")

    async def signInGroups(self):
        if self.config['SIGNINGROUP_CD'] == -1:
            self.log.log("INFO", "应援团签到任务已关闭")
            return
        self.log.log("INFO", "应援团签到任务开始")
        try:
            n = 0
            async for group in self.api.getGroups():
                if group['owner_uid'] == self.mid:
                    continue
                try:
                    await self.api.signInGroups(group['group_id'], group['owner_uid'])
                except Exception as e:
                    self.log.log("ERROR", group['group_name'] + " 签到失败")
                    self.errmsg.append(f"应援团签到失败: {e}")
                    continue
                self.log.log("DEBUG", group['group_name'] + " 签到成功")
                await asyncio.sleep(self.config['SIGNINGROUP_CD'] if self.config['SIGNINGROUP_CD'] > 0 else 0)
                n += 1
            if n:
                self.log.log("SUCCESS", f"应援团签到任务完成 {n}/{n}")
                self.message.append(f" 应援团签到任务完成 {n}/{n}")
            else:
                self.log.log("WARNING", "没有加入应援团")
        except Exception as e:
            self.log.exception(e)
            self.log.log("ERROR", "应援团签到任务失败: " + str(e))
            self.errmsg.append("应援团签到任务失败: " + str(e))

    async def doCustomSignIn(self):
        """
        自定义活动签到
        """
        if self.config.get('CUSTOMSIGNIN_CD') == -1:
            self.log.log("INFO", "自定义签到任务已关闭")
            return

        self.log.log("INFO", "自定义签到任务开始")
        try:
            n = 0
            for medal in self.medals:
                try:
                    await self.api.doCustomSignIn(medal['medal']['target_id'])
                    n += 1
                    self.log.log("SUCCESS", f"{medal['anchor_info']['nick_name']} 自定义签到成功")
                except Exception as e:
                    self.log.log("ERROR", f"{medal['anchor_info']['nick_name']} 自定义签到失败: {e}")
                    self.errmsg.append(f"【{self.name}】 {medal['anchor_info']['nick_name']} 自定义签到失败: {str(e)}")
                    continue
                await asyncio.sleep(self.config['CUSTOMSIGNIN_CD'] if self.config['CUSTOMSIGNIN_CD'] > 0 else 0)
            
            if n:
                self.log.log("SUCCESS", f"自定义签到任务完成 {n}/{len(self.medals)}")
                self.message.append(f"【{self.name}】 自定义签到任务完成 {n}/{len(self.medals)}")
            else:
                self.log.log("WARNING", "自定义签到任务完成 0/0")
        except Exception as e:
            self.log.exception(e)
            self.log.log("ERROR", "自定义签到任务失败: " + str(e))
            self.errmsg.append("自定义签到任务失败: " + str(e))
