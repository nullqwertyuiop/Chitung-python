import asyncio
import datetime
import json
import math
import os
import random
import time
from asyncio import Lock
from io import BytesIO
from pathlib import Path

from PIL import Image as PillowImage, ImageDraw
from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain, At
from graia.ariadne.message.parser.twilight import (
    Twilight,
    UnionMatch,
    MatchResult,
    SpacePolicy,
    RegexMatch,
    FullMatch,
)
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from .FishEnum import Waters, Time
from ..bank import vault, Currency
from ..utils.depends import BlacklistControl, FunctionControl


channel = Channel.current()

channel.name("ChitungFishing")
channel.author("角川烈&白门守望者 (Chitung-public), IshikawaKaito (Chitung-python)")
channel.description("七筒")

fishing_process_flag = []


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    FullMatch("/").space(SpacePolicy.NOSPACE),
                    UnionMatch("endfish", "collection", "fishhelp", "handbook")
                    @ "function",
                ]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            FunctionControl.enable(FunctionControl.Fish),
        ],
    )
)
async def chitung_fish_tool_handler(
    app: Ariadne,
    event: MessageEvent,
    function: MatchResult,
):
    if function.result.asDisplay() == "endfish":
        reply_msg = MessageChain.create([At(event.sender.id)])
        if event.sender.id in fishing_process_flag:
            reply_msg = reply_msg + Plain(text="已经停止钓鱼。")
            fishing_process_flag.remove(event.sender.id)
        else:
            reply_msg = reply_msg + Plain(text="您未在钓鱼中。")
        await app.sendGroupMessage(event.sender.group, reply_msg)

    elif function.result.asDisplay() == "collection":
        collected = get_collected(event.sender.id)
        collected = sum(fish_collected for fish_collected in collected)
        reply_msg = MessageChain.create(
            [
                At(event.sender.id),
                Plain(text=f"您的图鉴完成度目前为{round(collected * 100 / 72)}%\n\n"),
            ]
        )
        handbook_img = await async_get_handbook(event.sender.id)
        reply_msg += Image(data_bytes=handbook_img)
        await app.sendGroupMessage(event.sender.group, reply_msg)

    elif function.result.asDisplay() == "fishhelp":
        image_path = Path(assets_dir / "fishinfo.png")
        await app.sendGroupMessage(
            event.sender.group, MessageChain.create([Image(path=image_path)])
        )

    elif function.result.asDisplay() == "handbook":
        image_path = Path(assets_dir / "handbook.png")
        await app.sendGroupMessage(
            event.sender.group, MessageChain.create([Image(path=image_path)])
        )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    FullMatch("/fish"),
                    RegexMatch(r"\s*[AaBbCc]?") @ "pool",
                ]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            FunctionControl.enable(FunctionControl.Fish),
        ],
    )
)
async def chitung_fish_handler(
    app: Ariadne,
    event: MessageEvent,
    pool: MatchResult,
):
    global fishing_record
    water = pool.result.asDisplay().strip().upper()
    if event.sender.id in fishing_process_flag:
        await app.sendGroupMessage(event.sender.group, MessageChain("上次抛竿还在进行中。"))
    else:
        w = get_water(water)
        reply_msg = MessageChain.create(At(event.sender.id))
        if w != Waters.General:  # 非常规水域扣费
            if vault.has_enough_money(
                event.sender, Currency.CUCUMBER_PESO, FISHING_COST
            ):
                reply_msg = reply_msg + Plain(text=f"已收到您的捕鱼费用{FISHING_COST}黄瓜比索。")
            else:
                await app.sendGroupMessage(
                    event.sender.group,
                    MessageChain.create(reply_msg + Plain(text="您的黄瓜比索数量不够，请检查。")),
                )
                return

        now_ts = int(time.time())  # 精确到秒
        fishing_record = [
            start_time for start_time in fishing_record if start_time - now_ts < 3600
        ]
        record_in_one_hour = len(fishing_record)
        _time = 3 + random.randint(0, 3) + record_in_one_hour  # 线性增加时间
        item_number = 3 + random.randint(0, 1)
        fishing_record.append(now_ts)
        fishing_process_flag.append(event.sender.id)
        reply_msg = reply_msg + Plain(
            text=f"本次钓鱼预计时间为{_time}分钟。"
            f"麦氏渔业公司提醒您使用/fishhelp查询钓鱼功能的相关信息，如果长时间钓鱼未收杆，请使用/endfish 强制停止钓鱼。"
        )
        await app.sendGroupMessage(event.sender.group, MessageChain.create(reply_msg))
        # 这就是钓鱼开始了，在这躺下，躺够了起来
        await asyncio.sleep(_time * 60)
        # 起来一看，flag没了，被end了。
        if event.sender.id not in fishing_process_flag:
            return

        fish_map = get_item_id_randomly(item_number, w)
        reply_msg = MessageChain.create(At(event.sender.id), Plain(text="您钓到了：\n\n"))
        total_value = 0
        for fish_code, count in fish_map.items():
            fish = get_fish_by_code(fish_code)
            value = fish["price"] * count
            total_value += value
            reply_msg += f"{fish['name']}x{count}，价值{value}黄瓜比索\n"
        fish_img = await async_get_image(fish_map.keys())
        time_fix_coeff = 1.0 + record_in_one_hour * 0.05
        total_value = int(time_fix_coeff * total_value)
        reply_msg += f"\n时间修正系数为{time_fix_coeff}，共值{total_value}黄瓜比索。\n\n"
        reply_msg += Image(data_bytes=fish_img)
        vault.update_bank(event.sender.id, total_value, Currency.CUCUMBER_PESO)
        await save_record(event.sender.id, fish_map.keys())
        fishing_process_flag.remove(event.sender.id)
        await app.sendGroupMessage(event.sender.group, MessageChain.create(reply_msg))


async def collection(app: Ariadne, group: Group, member: Member):
    collected = get_collected(member.id)
    collected = sum(fish_collected for fish_collected in collected)
    reply_msg = MessageChain.create(
        [At(member.id), Plain(text=f"您的图鉴完成度目前为{round(collected * 100 / 72)}%\n\n")]
    )
    handbook_img = await async_get_handbook(member.id)
    reply_msg += Image(data_bytes=handbook_img)
    await app.sendGroupMessage(group, reply_msg)


def get_water(water: str):
    water = water.upper()
    if len(water) == 0:
        return Waters.General
    else:
        if water == "A":
            return Waters.Amur
        elif water == "B":
            return Waters.Caroline
        elif water == "C":
            return Waters.Chishima


def get_item_id_randomly(amount, w: Waters):
    fish_map = {}
    is_day_time = is_in_day_time()

    def filter_fish(fish_to_filter):
        if fish_to_filter["code"] // 100 != w.value:
            return False
        if fish_to_filter["time"] == Time.All.value:
            return True
        elif is_day_time and fish_to_filter["time"] == Time.Day.value:
            return True
        elif not is_day_time and fish_to_filter["time"] == Time.Night.value:
            return True

    actual_fish_list = list(filter(filter_fish, FISHING_LIST))
    # 降序第一
    max_price = sorted(actual_fish_list, key=lambda f: -f["price"])[0]["price"]

    weight_list = list(map(lambda f: max_price + 50 - f["price"], actual_fish_list))
    total_weight = sum(weight_list)

    for _ in range(amount):
        random_number = random.randint(0, total_weight)
        random_index = 0

        for fi, _ in enumerate(actual_fish_list):
            if random_number - weight_list[fi] < 0:
                random_index = fi
                break
            else:
                random_number = random_number - weight_list[fi]

        fish = actual_fish_list[random_index]
        if fish["code"] in fish_map:
            fish_map[fish["code"]] += 1
        else:
            fish_map[fish["code"]] = 1

    return fish_map


def calculate_daytime() -> tuple:
    """
    返回上海的日出日落时间datetime, (sunrise,sunset)
    """
    now = datetime.datetime.now()
    # 是否过了春分
    equinox = datetime.datetime.strptime(
        f"{now.year if now.month * 100 + now.day >= 321 else now.year - 1}-3-21",
        "%Y-%m-%d",
    ).date()

    gap_days = (datetime.datetime.now().date() - equinox).days.real
    days_of_year = 366 if now.year % 4 == 0 else 365
    theta1 = math.asin(
        math.sin(math.radians(360.0 * gap_days / days_of_year))
        * math.sin(math.radians(23 + 26.0 / 60 + 21.0 / 3600))
    )
    theta2 = math.asin(math.tan(math.radians(31.23)) * math.tan(theta1))
    time_sunrise = 6 - math.degrees(theta2) / 360 * 24 - (121.474 - 120) / 15
    time_sunset = 18 + math.degrees(theta2) / 360 * 24 - (121.474 - 120) / 15

    def to_datetime(decimal_float):
        """转换成对应今日的datetime"""
        int_part = math.floor(decimal_float)
        float_part = decimal_float - int_part
        hour = int_part
        minute = int(float_part * 60)
        dt = datetime.datetime(now.year, now.month, now.day, hour, minute, 0, 0)
        return dt

    return to_datetime(time_sunrise), to_datetime(time_sunset)


def is_in_day_time() -> bool:
    sun = calculate_daytime()
    now = datetime.datetime.now()
    return sun[0] < now < sun[1]


async def save_record(record_id, fish_list):
    await write_lock.acquire()
    records = load_fishing_records()
    for i, record in enumerate(records):
        if record["ID"] == record_id:
            collected = list(records[i]["recordList"])
            collected.extend(fish_list)
            records[i]["recordList"] = list(set(collected))
    with Path(record_dir).open("w", encoding="utf-8") as f:
        f.write(json.dumps({"singleRecords": records}, indent=4))
    write_lock.release()


def get_fish_by_code(code):
    return list(filter(lambda fish: fish["code"] == code, FISHING_LIST))[0]


def load_fishing_list():
    with Path(assets_dir / "FishingList.json").open("r", encoding="utf-8") as f:
        return json.loads(f.read())["fishingList"]


def load_fishing_records():
    with Path(record_dir).open("r", encoding="utf-8") as f:
        return json.loads(f.read())["singleRecords"]


def get_image(fish_list):
    fish_block = PillowImage.new(
        "RGBA", (32 * len(fish_list) + 20, 32 + 20), (12, 24, 30)
    )
    fish_block_draw = ImageDraw.ImageDraw(fish_block)
    fish_block_draw.rectangle(((0, 0), (32 * len(fish_list) + 20, 3)), fill="#FFCB48")
    fish_block_draw.rectangle(
        ((0, 32 + 20 - 3), (32 * len(fish_list) + 20, 32 + 20)), fill="#FFCB48"
    )
    fish_block = fish_block.convert("RGBA")
    for index, code in enumerate(fish_list):
        fish_image = PillowImage.open(
            assets_dir / "NormalFish" / f"{code}.png",
        ).convert("RGBA")
        fish_block.paste(
            fish_image, (index * 32 + 10, 10), mask=fish_image.split()[3]
        )  # mask 透明通道
    fish_block = fish_block.resize(
        (int(fish_block.size[0] * 2.5), int(fish_block.size[1] * 2.5)),
        resample=PillowImage.AFFINE,
    )
    bytes_io = BytesIO()
    fish_block.save(bytes_io, format="png")
    return bytes_io.getvalue()


async def async_get_image(fish_list):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_image, fish_list)


def get_records(record_id):
    records = load_fishing_records()
    for i, record in enumerate(records):
        if record["ID"] == record_id:
            return list(records[i]["recordList"])
    return []


def get_collected(record_id):
    collected = []
    records = get_records(record_id)
    for fish in FISHING_LIST:
        collected.append(fish["code"] in records)
    return collected


def get_handbook(record_id):
    handbook_template = PillowImage.open(assets_dir / "handbookTemplate.png")
    handbooks = PillowImage.new("RGBA", (32 * 8, 32 * 9), (62, 73, 72))
    vertical_count = 0
    horizontal_count = 0
    collected_list = get_collected(record_id)
    for index, fish_collected in enumerate(collected_list):
        fish_img_path = (
            assets_dir
            / f"{'NormalFish' if fish_collected else 'DarkFish'}"
            / f"{FISHING_LIST[index]['code']}.png"
        )
        fish_img = PillowImage.open(fish_img_path).convert("RGBA")
        handbooks.paste(
            fish_img,
            (vertical_count * 32, horizontal_count * 32),
            mask=fish_img.split()[3],
        )
        vertical_count = vertical_count + 1
        if vertical_count == 8:
            vertical_count = 0
            horizontal_count = horizontal_count + 1
    handbook_template.paste(handbooks, (45, 269))
    size = handbook_template.size
    handbook_template = handbook_template.resize(
        (int(size[0] * 2.5), int(size[1] * 2.5)), resample=PillowImage.AFFINE
    )
    bytes_io = BytesIO()
    handbook_template.save(bytes_io, format="png")
    return bytes_io.getvalue()


async def async_get_handbook(record_id):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_handbook, record_id)


assets_dir = Path(Path(__file__).parent / "assets" / "fishing")
record_dir = Path(Path(__file__).parent.parent / "data" / "fishRecord.json")
FISHING_LIST = load_fishing_list()
FISHING_COST = 800
fishing_record = []  # 为了计算过去一小时内的钓鱼人数，存时间戳
write_lock = Lock()

if not os.path.isfile(record_dir):
    with Path(record_dir).open("w", encoding="utf-8") as _:
        _.write(
            json.dumps({"singleRecords": [{"ID": 0, "recordList": [101]}]}, indent=4)
        )
