"""
弹幕打卡检测脚本（独立运行）
在 cron 指定时间检测主播是否开播：
  - 未开播  -> 发送弹幕打卡
  - 正在播  -> 不发弹幕（跳过）
  - 弹幕发够总条数 -> 跳过
共用 users.yaml 中的 access_key 配置，其余参数在下方写死。

说明：弹幕打卡在主播下播时依然能增加亲密度，因此本脚本选择
      在主播「未开播」时才发送弹幕，避免开播期间弹幕被淹没/风控。
"""
import json
import os
import sys
import time
import random
import asyncio
import logging
import warnings
from logging.handlers import TimedRotatingFileHandler
from aiohttp import ClientSession, ClientTimeout
from urllib.parse import urlencode
from hashlib import md5

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

# ============ 自定义参数 ============

# cron 表达式：
#   - 列表格式：CRON = ["0 9 * * *", "0 21 * * *"]
#   - 字符串格式，多个用 '||' 分割：CRON = "0 9 * * *||0 21 * * *"
CRON = "0 4 * * * || 0 10 * * * || 0 18 * * *"

# 弹幕间隔时间（秒），两次弹幕之间的间隔
DANMAKU_CD = 10

# 单次弹幕条数：每次任务中每个房间发送的弹幕条数
DANMAKU_COUNT = 5

# 总共弹幕条数：每个房间累计发送的弹幕上限，达到后跳过该房间
DANMAKU_TOTAL = 10

# 弹幕打卡轮询模式：
#   0 -> 顺序模式（一个房间发完单次条数再下一个）
#   1 -> 轮询模式（每轮每个房间发一条，发完再进入下一轮）
DANMAKU_ROUND_ROBIN = 1

# 自动跳过开关：
#   0 -> 不检测开播状态，无论是否开播都发弹幕
#   1 -> 主播离线时才发弹幕，在线时不发，避免打扰主播
SKIP_WHEN_LIVE = 1

# ====================================

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

log = logging.getLogger("danmaku_detect")
log.setLevel(logging.INFO)

log_format = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# 控制台输出
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_format)
log.addHandler(console_handler)

# 文件输出（按天轮转，保留30天）
file_handler = TimedRotatingFileHandler(
    filename=os.path.join(LOG_DIR, "test_danmaku.log"),
    when="midnight",
    interval=1,
    backupCount=30,
    encoding="utf-8",
)
file_handler.suffix = "%Y-%m-%d"
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(log_format)
log.addHandler(file_handler)

warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, as this time zone supports the fold attribute",
)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

APPKEY = "4409e2ce8ffd12b8"
APPSECRET = "59b43e04ad6965f34319062b478f83dd"

APP_HEADERS = {
    "User-Agent": "Mozilla/5.0 BiliDroid/6.73.1 (bbcallen@gmail.com) os/android model/Mi 10 Pro mobi_app/android build/6731100 channel/xiaomi innerVer/6731110 osVer/12 network/2",
    "Content-Type": "application/x-www-form-urlencoded",
}

WEB_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://live.bilibili.com/",
}

DANMAKUS = ["[花]", "[比心]"]


def sign_params(data: dict) -> dict:
    """对参数进行签名"""
    sorted_params = dict(sorted(data.items()))
    query_string = urlencode(sorted_params)
    sign = md5((query_string + APPSECRET).encode()).hexdigest()
    return {**sorted_params, "sign": sign}


def load_config():
    """加载 users.yaml 配置"""
    if os.environ.get("USERS"):
        return json.loads(os.environ.get("USERS"))
    import yaml
    with open("users.yaml", "r", encoding="utf-8") as f:
        return yaml.load(f, Loader=yaml.FullLoader)


# 内存缓存: mid -> {"date": str, "sent": {room_id: count}}
_cache = {}


def get_cache(mid):
    return _cache.setdefault(mid, {"date": "", "sent": {}})


async def login(session, access_key):
    """登录验证，返回 mid 和 name"""
    url = "https://app.bilibili.com/x/v2/account/mine"
    params = sign_params({
        "access_key": access_key,
        "actionKey": "appkey",
        "appkey": APPKEY,
        "ts": int(time.time()),
    })
    async with session.get(url, params=params, headers=APP_HEADERS) as resp:
        data = await resp.json()
        if data.get("code") != 0:
            raise Exception(f"登录失败: {data.get('message', '未知错误')}")
        info = data["data"]
        return info["mid"], info["name"]


async def get_medals(session, access_key):
    """获取用户所有粉丝勋章，返回 target_id -> medal 映射"""
    url = "https://api.live.bilibili.com/xlive/app-ucenter/v1/fansMedal/panel"
    medal_map = {}
    page = 1
    while True:
        params = sign_params({
            "access_key": access_key,
            "actionKey": "appkey",
            "appkey": APPKEY,
            "ts": int(time.time()),
            "page": page,
            "page_size": 50,
        })
        async with session.get(url, params=params, headers=APP_HEADERS) as resp:
            data = await resp.json()
            if data.get("code") != 0:
                raise Exception(f"获取勋章失败: {data.get('message', '未知错误')}")
            items = data["data"].get("list", [])
            for item in items:
                if item.get("room_info", {}).get("room_id", 0) != 0:
                    medal_map[item["medal"]["target_id"]] = item
            if not items:
                break
            page += 1
    return medal_map


async def get_live_users(session, access_key):
    """从动态页一次性获取正在直播的主播列表"""
    url = "https://api.bilibili.com/x/polymer/web-dynamic/v1/portal"
    try:
        async with session.get(url, params={"access_key": access_key}, headers=WEB_HEADERS) as resp:
            data = await resp.json()
            if data.get("code") != 0:
                log.warning(f"获取动态直播列表失败: {data.get('message', '未知错误')}")
                return []
            return data.get("data", {}).get("live_users", {}).get("items", [])
    except Exception as e:
        log.warning(f"获取动态直播列表异常: {e}")
        return []


async def send_danmaku(session, access_key, room_id):
    """发送一条弹幕"""
    url = "https://api.live.bilibili.com/xlive/app-room/v1/dM/sendmsg"
    params = sign_params({
        "access_key": access_key,
        "actionKey": "appkey",
        "appkey": APPKEY,
        "ts": int(time.time()),
    })
    data = {
        "cid": room_id,
        "msg": random.choice(DANMAKUS),
        "rnd": int(time.time()),
        "color": "16777215",
        "fontsize": "25",
    }
    async with session.post(url, params=params, data=data, headers=APP_HEADERS) as resp:
        result = await resp.json()
        if result.get("code") != 0:
            raise Exception(f"发送弹幕失败: {result.get('message', '未知错误')}")
        mode_info = result.get("data", {}).get("mode_info", {})
        extra = mode_info.get("extra", "{}")
        try:
            return json.loads(extra).get("content", "")
        except Exception:
            return ""


async def process_user(access_key):
    """处理单个用户的弹幕打卡"""
    session = ClientSession(timeout=ClientTimeout(total=10), trust_env=True)
    try:
        mid, name = await login(session, access_key)
        log.info(f"[{name}] {mid} 登录成功")

        medal_map = await get_medals(session, access_key)
        log.info(f"[{name}] 共有 {len(medal_map)} 个粉丝牌子")

        cache = get_cache(mid)
        today = time.strftime("%Y-%m-%d", time.localtime())
        if cache.get("date") != today:
            cache = {"date": today, "sent": {}}
            _cache[mid] = cache

        # 收集尚未发满总条数的目标房间
        targets = []
        for up_id, item in medal_map.items():
            room_id = int(item["room_info"]["room_id"])
            sent = cache["sent"].get(room_id, 0)
            if sent >= DANMAKU_TOTAL:
                log.info(f"[{name}] {item['anchor_info']['nick_name']} 已发满 {DANMAKU_TOTAL} 条，跳过")
                continue
            targets.append(item)

        if not targets:
            log.info(f"[{name}] 所有房间弹幕已发满，本轮跳过")
            return

        # 开启自动跳过时，一次性获取正在直播的主播 UID 集合
        live_uids = set()
        if SKIP_WHEN_LIVE == 1:
            live_users = await get_live_users(session, access_key)
            live_uids = {int(u["mid"]) for u in live_users if "mid" in u}
            log.info(f"[{name}] 当前正在直播的主播 {len(live_uids)} 个")

        for item in targets:
            room_id = int(item["room_info"]["room_id"])
            uname = item["anchor_info"]["nick_name"]
            up_id = int(item["medal"]["target_id"])

            if SKIP_WHEN_LIVE == 1:
                # 开启自动跳过：没开播才发弹幕，正在播则跳过
                if up_id in live_uids:
                    log.info(f"[{name}] {uname} 正在直播，跳过发弹幕")
                    continue

            # 未开播（或关闭检测），执行弹幕打卡
            remaining = DANMAKU_TOTAL - cache["sent"].get(room_id, 0)
            count = min(DANMAKU_COUNT, remaining)
            log.info(f"[{name}] {uname} 未开播，发送 {count} 条弹幕 (累计 {cache['sent'].get(room_id, 0)}/{DANMAKU_TOTAL})")

            if DANMAKU_ROUND_ROBIN:
                # 轮询模式：该房间本轮每次发一条
                for i in range(count):
                    try:
                        content = await send_danmaku(session, access_key, room_id)
                        cache["sent"][room_id] = cache["sent"].get(room_id, 0) + 1
                        log.info(f"[{name}] {uname} 弹幕发送成功: {content} ({cache['sent'][room_id]}/{DANMAKU_TOTAL})")
                    except Exception as e:
                        log.error(f"[{name}] {uname} 弹幕发送失败: {e}")
                    if i < count - 1:
                        await asyncio.sleep(DANMAKU_CD)
            else:
                # 顺序模式：单次条数内连续发送
                for i in range(count):
                    try:
                        content = await send_danmaku(session, access_key, room_id)
                        cache["sent"][room_id] = cache["sent"].get(room_id, 0) + 1
                        log.info(f"[{name}] {uname} 弹幕发送成功: {content} ({cache['sent'][room_id]}/{DANMAKU_TOTAL})")
                    except Exception as e:
                        log.error(f"[{name}] {uname} 弹幕发送失败: {e}")
                    if i < count - 1:
                        await asyncio.sleep(DANMAKU_CD)

            # 房间之间也间隔一个 CD
            await asyncio.sleep(DANMAKU_CD)

        log.info(f"[{name}] 本轮弹幕打卡完成")
    except Exception as e:
        log.error(f"[{name}] 处理异常: {e}")
    finally:
        await session.close()


def run():
    """执行一轮弹幕打卡任务"""
    config = load_config()

    log.info(
        f"弹幕打卡任务启动，cron={CRON}，间隔={DANMAKU_CD}s，"
        f"单次={DANMAKU_COUNT}条，总={DANMAKU_TOTAL}条，"
        f"轮询模式={'开' if DANMAKU_ROUND_ROBIN else '关'}，"
        f"自动跳过={'开' if SKIP_WHEN_LIVE == 1 else '关'}"
    )

    async def _run():
        tasks = []
        for user in config.get("USERS", []):
            access_key = user.get("access_key", "")
            if access_key:
                tasks.append(process_user(access_key))
        if not tasks:
            log.error("未找到有效的用户配置")
            return
        await asyncio.gather(*tasks)

    asyncio.run(_run())


if __name__ == "__main__":
    # 解析多 cron 表达式：支持列表格式或 '||' 分割的字符串
    if isinstance(CRON, list):
        cron_list = CRON
    elif isinstance(CRON, str):
        cron_list = CRON.split("||")
    else:
        log.error(f"CRON 格式错误: {CRON}")
        cron_list = []

    scheduler = BlockingScheduler()
    job_count = 0
    for index, cron_expr in enumerate(cron_list):
        cron_expr = cron_expr.strip()
        if not cron_expr:
            continue
        try:
            scheduler.add_job(
                run,
                CronTrigger.from_crontab(cron_expr),
                misfire_grace_time=3600,
                max_instances=2,
            )
            log.info(f"已添加定时任务: [{cron_expr}] (第 {index + 1}/{len(cron_list)} 个)")
            job_count += 1
        except Exception as e:
            log.error(f"Cron 表达式 [{cron_expr}] 格式错误或添加失败: {e}")

    if job_count > 0:
        log.info("所有定时任务已启动，等待执行...")
        scheduler.start()
    else:
        log.error("未成功添加任何定时任务，请检查 CRON 配置")
