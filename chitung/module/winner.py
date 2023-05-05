from io import BytesIO
from pathlib import Path

from creart import it
from graia.amnesia.message import MessageChain, Text
from graia.saya import Channel
from graiax.shortcut import decorate, listen
from graiax.shortcut.text_parser import MatchRegex
from ichika.client import Client
from ichika.core import Group, Member
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
async def winner_handler(client: Client, group: Group, member: Member):
    await client.send_group_message(
        group.uin,
        MessageChain([Text(f"Ok Winner! {member.card_name}\n\n（框架还没支持获取群员列表所以先这样了）")]),
    )
    avatar = PillowImage.open(BytesIO(await get_avatar(member.uin))).resize((512, 512))
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
