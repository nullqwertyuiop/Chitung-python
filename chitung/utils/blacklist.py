import json
import os
from pathlib import Path
from typing import Literal

from aiohttp import ClientResponseError
from graia.ariadne import get_running
from graia.ariadne.adapter import Adapter
from loguru import logger

from ..utils.models import BlacklistModel

if not os.path.isdir(Path(Path(__file__).parent) / "data"):
    os.mkdir(Path(Path(__file__).parent) / "data")


def load_blacklist() -> BlacklistModel:
    if os.path.isfile(Path(Path(__file__).parent.parent) / "data" / "Blacklist.json"):
        with open(Path(Path(__file__).parent.parent) / "data" / "Blacklist.json", "r", encoding="utf-8") as f:
            bl = BlacklistModel(**json.loads(f.read()))
    else:
        bl = BlacklistModel()
    return bl


def store_blacklist():
    with open(Path(Path(__file__).parent.parent) / "data" / "Blacklist.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(blacklist.dict(), indent=4, ensure_ascii=False))


blacklist: BlacklistModel = load_blacklist()
store_blacklist()


def add_blacklist(target_id: int, target_type: Literal["friend", "group"]) -> bool:
    if target_type == "friend":
        if target_id in blacklist.friendBlacklist:
            return False
        blacklist.friendBlacklist.append(target_id)
    else:
        if target_id in blacklist.groupBlacklist:
            return False
        blacklist.groupBlacklist.append(target_id)
    store_blacklist()
    return True


def remove_blacklist(target_id: int, target_type: Literal["friend", "group"]):
    if target_type == "friend":
        if target_id not in blacklist.friendBlacklist:
            return False
        blacklist.friendBlacklist.remove(target_id)
    else:
        if target_id not in blacklist.groupBlacklist:
            return False
        blacklist.groupBlacklist.remove(target_id)
    store_blacklist()
    return True


async def get_remote_blacklist():
    try:
        async with get_running(Adapter).session.get("https://api.nullqwertyuiop.me/universal/getBotList") as resp:
            bot_list = await resp.json()
        for _, bots in bot_list.items():
            for bot in bots:
                if bot["id"] not in blacklist.remoteBlacklist:
                    blacklist.remoteBlacklist.append(bot["id"])
    except ClientResponseError:
        logger.error("Error occurred when attempting to connect to api.nullqwertyuiop.me")
    try:
        async with get_running(Adapter).session.get("https://api.tail.icu/api/v1/ill/getAll") as resp:
            targets = (await resp.json())["data"]["list"]
        for target in targets:
            target = int(target)
            if target not in blacklist.remoteBlacklist:
                blacklist.remoteBlacklist.append(target)
    except ClientResponseError:
        logger.error("Error occurred when attempting to connect to api.tail.icu")
    store_blacklist()
