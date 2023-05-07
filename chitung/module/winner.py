from datetime import datetime
from io import BytesIO
from pathlib import Path

from creart import it
from graia.amnesia.message import MessageChain, Text
from graia.saya import Channel
from graiax.shortcut import decorate, listen
from graiax.shortcut.text_parser import MatchRegex
from ichika.client import Client
from ichika.core import Group
from ichika.graia.event import GroupMessage
from ichika.message.elements import Image
from PIL import Image as PillowImage

from chitung.core.decorator import FunctionType, Switch
from chitung.core.session import SessionContainer

channel = Channel.current()


@listen(GroupMessage)
@decorate(
    MatchRegex(r"^(?:\/|(?:\/?[Oo][Kk] ?))winner$"),
    Switch.check(GroupMessage, FunctionType.LOTTERY),
)
async def winner_handler(client: Client, group: Group):
    member_list = await client.get_member_list(group.uin)
    now = datetime.now()
    guy_of_the_day = member_list[
        int(
            (now.year + now.month * 10000 + now.day * 1000000)
            * 100000000000
            / group.uin
            % len(member_list)
        )
    ]
    name = guy_of_the_day.card_name or guy_of_the_day.nickname
    await client.send_group_message(
        group.uin,
        MessageChain([Text(f"Ok Winner! {name}")]),
    )
    avatar = PillowImage.open(BytesIO(await get_avatar(guy_of_the_day.uin))).resize(
        (512, 512)
    )
    base = PillowImage.open(Path("chitung") / "assets" / "winner" / "wanted.jpg")
    base.paste(avatar, (94, 251))
    output = BytesIO()
    base.save(output, "jpeg")
    await client.send_group_message(
        group.uin,
        MessageChain(
            [
                Image.build(output.getvalue()),
            ]
        ),
    )


async def get_avatar(uin: int) -> bytes:
    session = it(SessionContainer).get(channel.module)
    async with session.get(
        f"https://q2.qlogo.cn/headimg_dl?dst_uin={uin}&spec=640"
    ) as resp:
        return await resp.read()
