import random
import re
from datetime import datetime
from pathlib import Path

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.message.element import Plain, At
from graia.ariadne.message.parser.twilight import Twilight, UnionMatch, WildcardMatch
from graia.ariadne.model import Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from ..utils.depends import BlacklistControl, FunctionControl

channel = Channel.current()

channel.name("ChitungFortuneTeller")
channel.author("角川烈&白门守望者 (Chitung-public), nullqwertyuiop (Chitung-python)")
channel.description("这就是你今天的签")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[
            Twilight(
                [WildcardMatch().flags(re.S), UnionMatch("求签", "麻将"), WildcardMatch()]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            FunctionControl.enable(FunctionControl.Responder),
        ],
    )
)
async def chitung_fortune_teller_handler(app: Ariadne, event: MessageEvent):
    supplicant = event.sender
    now = datetime.now()
    random.seed(int(f"{supplicant.id}{now.year * 1000}{now.month * 100}{now.day}"))
    if random.random() <= 0.02:
        await app.sendMessage(
            event.sender.group if isinstance(event, GroupMessage) else event.sender,
            MessageChain.create(
                [
                    At(supplicant)
                    if isinstance(supplicant, Member)
                    else Plain(text=f"@{supplicant.nickname}"),
                    Plain(text="\n今天的占卜麻将牌是: 寄\n运势是: " "寄吧\n是寄吧，寄吧寄吧寄吧"),
                    Image(path=Path(assets_dir / "寄.jpg")),
                ]
            ),
        )
    mahjong_of_the_day = random.randint(1, 144)
    if mahjong_of_the_day < 36:
        mahjong_numero = mahjong_of_the_day % 9
        mahjong = chinese_num[mahjong_of_the_day % 9] + "筒"
    elif mahjong_of_the_day < 72:
        mahjong_numero = (mahjong_of_the_day - 36) % 9 + 9
        mahjong = chinese_num[mahjong_of_the_day % 9] + "条"
    elif mahjong_of_the_day < 108:
        mahjong_numero = (mahjong_of_the_day - 72) % 9 + 18
        mahjong = chinese_num[mahjong_of_the_day % 9] + "萬"
    elif mahjong_of_the_day < 124:
        mahjong_numero = (mahjong_of_the_day - 108) % 4 + 27
        mahjong = feng_xiang[mahjong_of_the_day % 4] + "风"
    elif mahjong_of_the_day < 136:
        mahjong_numero = (mahjong_of_the_day - 124) % 3 + 31
        mahjong = zhong_fa_bai[mahjong_of_the_day % 3]
    else:
        mahjong_numero = mahjong_of_the_day - 102
        mahjong = f"花牌（{hua_pai[mahjong_of_the_day - 136]}）"
    pre_chain = (
        [At(supplicant), Plain(text="\n")] if isinstance(supplicant, Member) else []
    )
    colour = "Red" if random.randrange(2) else "Yellow"
    image_path = Path(assets_dir / colour / f"{mahjong}.png")
    await app.sendMessage(
        event.sender.group if isinstance(event, GroupMessage) else event.sender,
        MessageChain.create(
            pre_chain
            + [
                Plain(
                    text=f"今天的占卜麻将牌是: {mahjong}\n运势是: "
                    f"{luck[mahjong_numero]}\n{saying[mahjong_numero]}"
                ),
                Image(path=image_path),
            ]
        ),
    )


# <editor-fold desc="Texts">
chinese_num = ["一", "二", "三", "四", "五", "六", "七", "八", "九"]
feng_xiang = ["東", "南", "西", "北"]
zhong_fa_bai = ["红中", "發财", "白板"]
hua_pai = ["春", "夏", "秋", "冬", "梅", "兰", "竹", "菊"]
luck = [
    "大凶",
    "末吉",
    "吉",
    "吉凶相半",
    "吉",
    "末吉",
    "大大吉",
    "吉",
    "小凶後吉",
    "吉",
    "末吉",
    "吉",
    "小凶後吉",
    "吉",
    "末吉",
    "大吉",
    "吉凶相半",
    "吉",
    "末吉",
    "半吉",
    "凶後吉",
    "半吉",
    "末吉",
    "半吉",
    "大凶",
    "半吉",
    "吉凶相半",
    "半吉",
    "末吉",
    "凶後大吉",
    "凶後吉",
    "小吉",
    "小凶後吉",
    "大吉",
    "吉凶相半",
    "小吉",
    "末吉",
    "小吉",
    "大吉",
    "中吉",
    "大吉",
    "中吉",
]
saying = [
    "别出门了，今天注意安全。",
    "是吉是凶并不清楚，暂定为吉！",
    "还算不错！",
    "吉凶各一半，要小心哦！",
    "其实还不错！",
    "是吉是凶并不清楚，暂定为吉！",
    "实现愿望的最高幸运，今天你会心想事成！",
    "还不错！",
    "丢失的运气会补回来的！",
    "还不错！",
    "是吉是凶并不清楚，暂定为吉！",
    "还可以的！",
    "丢失的运气会补回来的！",
    "还不错！",
    "是吉是凶并不清楚，暂定为吉！",
    "是仅次于大大吉的超级好运！",
    "吉凶各一半，要小心哦！",
    "还不错！",
    "是吉是凶并不清楚，暂定为吉！",
    "勉勉强强的好运！",
    "一阵不走运之后会好运的！",
    "勉勉强强的好运！",
    "是吉是凶并不清楚，暂定为吉！",
    "勉勉强强的好运！",
    "别出门了，今天注意安全。",
    "勉勉强强的好运！",
    "吉凶各一半，小心一些总不会错！",
    "勉勉强强的好运！",
    "是吉是凶并不清楚，暂定为吉！",
    "一阵不走运之后会行大运的！",
    "一阵不走运之后会好运的！",
    "微小但一定会到来的好运！",
    "丢失的运气会补回来的！",
    "是仅次于大大吉的超级好运！会有很好的财运！",
    "吉凶各一半，要小心哦！",
    "微小但一定会到来的好运！",
    "是吉是凶并不清楚，暂定为吉！",
    "微小但一定会到来的好运！",
    "是仅次于大大吉的超级好运！",
    "非常好的运气！",
    "是仅次于大大吉的超级好运！",
    "非常好的运气！姻缘不错！",
]
# </editor-fold>
assets_dir = Path(Path(__file__).parent / "assets" / "mahjong")
