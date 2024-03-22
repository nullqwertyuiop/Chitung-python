import random
from contextlib import contextmanager
from datetime import datetime
from hashlib import md5
from pathlib import Path

from avilla.core import Context, Picture, Selector
from avilla.standard.core.message import MessageReceived
from avilla.twilight.twilight import Twilight, UnionMatch, WildcardMatch
from graia.amnesia.message import MessageChain, Text
from graia.saya.builtins.broadcast.shortcut import dispatch, listen

from .const import (
    ASSETS_DIR,
    CHINESE_NUM,
    FENG_XIANG,
    HUA_PAI,
    LUCK,
    SAYING,
    ZHONG_FA_BAI,
)


@contextmanager
def seed(target: Selector):
    now = datetime.now()
    hashed = int(md5(target.last_value.encode()).hexdigest(), 16)
    random.seed(int(f"{hashed}{now.year * 1000}{now.month * 100}{now.day}"))
    yield
    random.seed()


def build_chain(target: Selector) -> MessageChain:
    if random.random() <= 0.02:
        return MessageChain(
            [
                Text("今天的占卜麻将牌是: 寄\n运势是: 寄吧\n是寄吧，寄吧寄吧寄吧"),
                Picture(Path(ASSETS_DIR / "寄.jpg")),
            ]
        )

    with seed(target):
        mahjong_of_the_day = random.randint(1, 144)
        if mahjong_of_the_day < 36:
            mahjong_num = mahjong_of_the_day % 9
            mahjong = f"{CHINESE_NUM[mahjong_of_the_day % 9]}筒"
        elif mahjong_of_the_day < 72:
            mahjong_num = (mahjong_of_the_day - 36) % 9 + 9
            mahjong = f"{CHINESE_NUM[mahjong_of_the_day % 9]}条"
        elif mahjong_of_the_day < 108:
            mahjong_num = (mahjong_of_the_day - 72) % 9 + 18
            mahjong = f"{CHINESE_NUM[mahjong_of_the_day % 9]}萬"
        elif mahjong_of_the_day < 124:
            mahjong_num = (mahjong_of_the_day - 108) % 4 + 27
            mahjong = f"{FENG_XIANG[mahjong_of_the_day % 4]}风"
        elif mahjong_of_the_day < 136:
            mahjong_num = (mahjong_of_the_day - 124) % 3 + 31
            mahjong = ZHONG_FA_BAI[mahjong_of_the_day % 3]
        else:
            mahjong_num = mahjong_of_the_day - 102
            mahjong = f"花牌（{HUA_PAI[mahjong_of_the_day - 136]}）"
        colour = "Red" if random.randrange(2) else "Yellow"
        return MessageChain(
            [
                Text(
                    f"今天的占卜麻将牌是: {mahjong}\n运势是: "
                    f"{LUCK[mahjong_num]}\n{SAYING[mahjong_num]}"
                ),
                Picture(Path(ASSETS_DIR / colour / f"{mahjong}.png")),
            ]
        )


@listen(MessageReceived)
@dispatch(Twilight(WildcardMatch(), UnionMatch("求签", "麻将"), WildcardMatch()))
async def fortune_teller(ctx: Context):
    await ctx.scene.send_message(build_chain(ctx.client))
