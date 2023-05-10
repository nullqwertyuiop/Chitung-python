import random

from graia.amnesia.message import MessageChain, Text
from graiax.shortcut import decorate, listen
from graiax.shortcut.text_parser import MatchRegex
from ichika.client import Client
from ichika.core import Group, Member
from ichika.graia.event import GroupMessage
from ichika.message.elements import At

from chitung.core.decorator import FunctionType, Switch


@listen(GroupMessage)
@decorate(
    MatchRegex(r"^(?:\/|(?:\/?[Oo][Kk] ?))bummer"),
    Switch.check(GroupMessage, FunctionType.LOTTERY),
)
async def bummer_handler(client: Client, group: Group, member: Member):
    if (await client.get_member(group.uin, client.uin)).permission not in (1, 2):
        return await client.send_group_message(
            group.uin, MessageChain([Text("七筒目前还没有管理员权限，请授予七筒权限解锁更多功能。")])
        )
    member_list = await client.get_member_list(group.uin)
    if not (normal_members := [m for m in member_list if m.permission not in (1, 2)]):
        return await client.send_group_message(
            group.uin, MessageChain([Text("全都是管理员的群你让我抽一个普通成员禁言？别闹。")])
        )
    victim: Member = random.choice(normal_members)
    await client.mute_member(group.uin, victim.uin, 120)
    if member.permission not in (1, 2):
        if member.id != victim.id:
            await client.mute_member(group.uin, member.uin, 120)
            await client.send_group_message(
                group.uin,
                MessageChain(
                    [
                        Text(f"Ok Bummer! {victim.card_name}\n"),
                        At(target=member.uin, display=f"@{member.card_name}"),
                        Text(" 以自己为代价随机带走了 "),
                        At(target=victim.uin, display=f"@{victim.card_name}"),
                    ]
                ),
            )
            return
        return await client.send_group_message(
            group.uin,
            MessageChain(
                [
                    Text(
                        text=f"Ok Bummer! {victim.card_name}\n"
                        f"{member.card_name} 尝试随机极限一换一。他成功把自己换出去了！"
                    )
                ]
            ),
        )
    await client.send_group_message(
        group.uin,
        MessageChain(
            [
                Text(f"Ok Bummer! {victim.card_name}\n管理员"),
                At(target=member.uin, display=f"@{member.card_name}"),
                Text(" 随机带走了 "),
                At(target=victim.uin, display=f"@{victim.card_name}"),
            ]
        ),
    )
