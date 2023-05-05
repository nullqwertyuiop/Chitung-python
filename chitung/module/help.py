from pathlib import Path

from graia.amnesia.message import MessageChain
from graiax.shortcut import decorate, listen
from graiax.shortcut.text_parser import MatchRegex
from ichika.client import Client
from ichika.core import Friend, Group
from ichika.graia.event import FriendMessage, GroupMessage
from ichika.message.elements import Image

from chitung.core.decorator import FunctionType, Switch


@listen(GroupMessage)
@decorate(
    MatchRegex(r"^/help$"),
    Switch.check(GroupMessage, FunctionType.RESPONDER),
)
async def group_help_image_handler(client: Client, group: Group):
    await client.send_group_message(
        group.uin,
        MessageChain([Image.build(Path("chitung") / "assets" / "help" / "funct.png")]),
    )


@listen(FriendMessage)
@decorate(
    MatchRegex(r"^/help$"),
    Switch.check(FriendMessage, FunctionType.RESPONDER),
)
async def friend_help_image_handler(client: Client, friend: Friend):
    await client.send_friend_message(
        friend.uin,
        MessageChain([Image.build(Path("chitung") / "assets" / "help" / "funct.png")]),
    )
