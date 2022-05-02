import asyncio
import datetime
import json
import math
import random
import time
from pathlib import Path

from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain, At
from graia.ariadne.message.parser.twilight import Twilight, UnionMatch, MatchResult, SpacePolicy, RegexMatch
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from chitung.bank import vault, Currency
from .waters import Waters
from ..utils.depends import BlacklistControl

channel = Channel.current()

channel.name("ChitungLottery")
channel.author("角川烈&白门守望者 (Chitung-public)，IshikawaKaito (Chitung-python)")
channel.description("七筒")

fishing_process_flag = []


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("/").space(SpacePolicy.NOSPACE),
                    UnionMatch("endfish", "collection", "fishhelp", "handbook") @ "function",
                ]
            )
        ],
        decorators=[BlacklistControl.enable()]
    )
)
async def chitung_fish_tool_handler(
        app: Ariadne,
        event: MessageEvent,
        function: MatchResult,
):
    if function.result.asDisplay() == "endfish":
        await endfish(app, event.sender.group, event.sender)
    elif function.result.asDisplay() == "collection":
        await collection(app, event.sender.group, event.sender)
    elif function.result.asDisplay() == "fishhelp":
        await fishhelp(app, event)
    elif function.result.asDisplay() == "handbook":
        await handbook(app, event)


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    RegexMatch(r"/fish\s*[AaBbCc]{0,1}") @ "fish_command",
                ]
            )
        ],
        decorators=[BlacklistControl.enable()]
    )
)
async def chitung_fish_handler(
        app: Ariadne,
        event: MessageEvent,
        fish_command: MatchResult,
):
    global fishing_record
    water = fish_command.result.asDisplay().replace("/fish", "").strip().upper()
    if event.sender.id in fishing_process_flag:
        await app.sendGroupMessage(event.sender.group, MessageChain.create(
            [Plain(text="上次抛竿还在进行中。")]
        ))
    else:
        w = get_water(water)
        reply_msg = MessageChain.create(At(event.sender.id))
        if w != Waters.General:  # 非常规水域扣费
            if vault.has_enough_money(event.sender, Currency.PUMPKIN_PESO, FISHING_COST):
                reply_msg = reply_msg + Plain(text=f"已收到您的捕鱼费用{FISHING_COST}南瓜比索。")
            else:
                await app.sendGroupMessage(event.sender.group, MessageChain.create(
                    reply_msg + Plain(text="您的南瓜比索数量不够，请检查。")
                ))
                return

        now_ts = int(time.time())  # 精确到秒
        fishing_record = [start_time for start_time in fishing_record if start_time - now_ts < 3600]
        record_in_one_hour = len(fishing_record)
        _time = 3 + random.randint(0, 3) + record_in_one_hour  # 线性增加时间
        item_number = 3 + random.randint(0, 1)
        fishing_record.append(now_ts)
        fishing_process_flag.append(event.sender.id)
        reply_msg = reply_msg + Plain(
            text=f"本次钓鱼预计时间为{_time}分钟。"
                 f"麦氏渔业公司提醒您使用/fishhelp查询钓鱼功能的相关信息，如果长时间钓鱼未收杆，请使用/endfish 强制停止钓鱼。"
        )
        await app.sendGroupMessage(event.sender.group, MessageChain.create(
            reply_msg
        ))
        # 这就是钓鱼开始了，在这躺下，躺够了起来
        await asyncio.sleep(_time * 60)
        # 起来一看，flag没了，被end了。
        if event.sender.id not in fishing_process_flag:
            return


async def endfish(app: Ariadne, group: Group, member: Member):
    reply_msg = MessageChain.create(At(member.id))
    if member.id in fishing_process_flag:
        reply_msg = reply_msg + Plain(text="已经停止钓鱼。")
        fishing_process_flag.remove(member.id)
    else:
        reply_msg = reply_msg + Plain(text="您未在钓鱼中。")
    await app.sendGroupMessage(group, reply_msg)


async def collection(app: Ariadne, group: Group, member: Member):
    return


async def fishhelp(app: Ariadne, event: MessageEvent):
    image_path = Path(assets_dir / "fishinfo.png")
    await app.sendGroupMessage(
        event.sender.group, MessageChain.create(
            [Image(path=image_path)]
        )
    )


async def handbook(app: Ariadne, event: MessageEvent):
    image_path = Path(assets_dir / "handbook.png")
    await app.sendGroupMessage(
        event.sender.group, MessageChain.create(
            [Image(path=image_path)]
        )
    )


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


def get_item_id_randomly(amount, waters):
    fish_map = {}


def calculate_daytime() -> tuple:
    """
    返回上海的日出日落时间datetime, (sunrise,sunset)
    """
    now = datetime.datetime.now()
    # 是否过了春分
    equinox = datetime.datetime.strptime(
        f"{now.year if now.month * 100 + now.day >= 321 else now.year - 1}-3-21", '%Y-%m-%d'
    ).date()

    gap_days = (datetime.datetime.now().date() - equinox).days.real
    days_of_year = 366 if now.year % 4 == 0 else 365
    theta1 = math.asin(
        math.sin(math.radians(360.0 * gap_days / days_of_year)) * math.sin(math.radians(23 + 26.0 / 60 + 21.0 / 3600)))
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


def load_fishing_list():
    with Path(assets_dir / "FishingList.json").open("r", encoding="utf-8") as f:
        return json.loads(f.read())


assets_dir = Path(Path(__file__).parent / "assets" / "fishing")
FISHING_LIST = load_fishing_list()
FISHING_COST = 800
fishing_record = []  # 为了计算过去一小时内的钓鱼人数，存时间戳

if __name__ == '__main__':
    calculate_daytime()
