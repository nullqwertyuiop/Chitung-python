from pathlib import Path

from graia.amnesia.message import MessageChain
from graiax.shortcut import decorate, listen
from graiax.shortcut.text_parser import MatchRegex
from ichika.client import Client
from ichika.core import Friend, Group
from ichika.graia.event import FriendMessage, GroupMessage
from ichika.message.elements import Image

from chitung.core.decorator import FunctionType, Switch
from chitung.core.util import send_message


@listen(GroupMessage, FriendMessage)
@decorate(
    MatchRegex(r"^/help$"),
    Switch.check(FunctionType.RESPONDER),
)
async def simple_help_image_handler(client: Client, target: Group | Friend):
    await send_message(
        client,
        target,
        MessageChain([Image.build(Path("chitung") / "assets" / "help" / "funct.png")]),
    )
