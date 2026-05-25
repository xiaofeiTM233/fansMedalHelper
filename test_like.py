"""
动态页开播检测点赞脚本
独立运行，每60秒轮询一次动态页API，检测正在直播的主播
如果用户有对应粉丝牌子，则执行点赞任务，每天每个主播只执行一次
共用 users.yaml 中的 LIKE_CD 和 LIKE_COUNT 配置
"""
import json
import os
import sys
import time
import asyncio
import logging
import warnings
from aiohttp import ClientSession, ClientTimeout
from urllib.parse import urlencode
from hashlib import md5

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("live_detect")

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
    "Referer": "https://www.bilibili.com/",
}

POLL_INTERVAL = 60


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


def load_cache(mid):
    path = f"live_detect_cache_{mid}.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"date": "", "liked_uids": []}


def save_cache(mid, cache):
    path = f"live_detect_cache_{mid}.json"
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    except Exception as e:
        log.warning(f"保存缓存失败: {e}")


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
    """从动态页获取正在直播的主播列表"""
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


async def like(session, access_key, room_id, up_id, self_uid):
    """执行一次点赞"""
    url = "https://api.live.bilibili.com/xlive/app-ucenter/v1/like_info_v3/like/likeReportV3"
    data = sign_params({
        "access_key": access_key,
        "actionKey": "appkey",
        "appkey": APPKEY,
        "click_time": 1,
        "room_id": room_id,
        "anchor_id": up_id,
        "uid": up_id,
    })
    async with session.post(url, data=data, headers=APP_HEADERS) as resp:
        result = await resp.json()
        if result.get("code") != 0:
            raise Exception(f"点赞失败: {result.get('message', '未知错误')}")


async def process_user(access_key, like_count, like_cd):
    """处理单个用户的动态检测点赞"""
    session = ClientSession(timeout=ClientTimeout(total=10), trust_env=True)
    try:
        mid, name = await login(session, access_key)
        log.info(f"[{name}] {mid} 登录成功")

        medal_map = await get_medals(session, access_key)
        log.info(f"[{name}] 共有 {len(medal_map)} 个粉丝牌子")

        cache = load_cache(mid)
        today = time.strftime("%Y-%m-%d", time.localtime())
        if cache.get("date") != today:
            cache = {"date": today, "liked_uids": []}
            save_cache(mid, cache)

        while True:
            live_users = await get_live_users(session, access_key)

            if not live_users:
                log.debug(f"[{name}] 动态页没有检测到正在直播的主播，等待下次轮询")
                await asyncio.sleep(POLL_INTERVAL)
                continue

            liked_count = 0
            for live_user in live_users:
                uid = live_user["mid"]
                room_id = live_user["room_id"]
                uname = live_user["uname"]

                if uid in cache["liked_uids"]:
                    continue
                if uid not in medal_map:
                    continue

                log.info(f"[{name}] 检测到 {uname} 正在直播，有粉丝牌子，开始点赞 ({like_count}次)...")
                try:
                    for i in range(like_count):
                        await like(session, access_key, room_id, uid, mid)
                        if like_cd > 0:
                            await asyncio.sleep(like_cd)
                    log.info(f"[{name}] {uname} 点赞完成")
                    cache["liked_uids"].append(uid)
                    liked_count += 1
                    await asyncio.sleep(like_cd)
                except Exception as e:
                    log.error(f"[{name}] {uname} 点赞失败: {e}")

            if liked_count > 0:
                save_cache(mid, cache)
                log.info(f"[{name}] 本轮检测完成，为 {liked_count} 个主播点赞")

            await asyncio.sleep(POLL_INTERVAL)
    except Exception as e:
        log.error(f"用户处理异常退出: {e}")
    finally:
        await session.close()


async def main():
    config = load_config()

    like_cd = 15 #config.get("LIKE_CD", 3)
    like_count = 500 #config.get("LIKE_COUNT", 500)

    if like_count == 0 or like_cd == -1:
        log.warning("LIKE_COUNT=0 或 LIKE_CD=-1，点赞功能未开启，请先配置")
        return

    log.info(f"动态开播检测点赞启动，轮询间隔 {POLL_INTERVAL} 秒，每次点赞 {like_count} 次，间隔 {like_cd} 秒")

    tasks = []
    for user in config.get("USERS", []):
        access_key = user.get("access_key", "")
        if access_key:
            tasks.append(process_user(access_key, like_count, like_cd))

    if not tasks:
        log.error("未找到有效的用户配置")
        return

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
