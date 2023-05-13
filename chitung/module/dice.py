import random
import re

from graia.amnesia.message import MessageChain, Text
from graiax.shortcut import decorate, listen
from graiax.shortcut.text_parser import MatchRegex
from ichika.client import Client
from ichika.core import Group
from ichika.graia.event import GroupMessage

from chitung.core.decorator import FunctionType, Switch
from chitung.core.util import send_message

SINGLE_REGEX_STR = r"(?:[./][Dd](?:ice)? ?)([1-9]\d{0,7})"


@listen(GroupMessage)
@decorate(
    MatchRegex(rf"^{SINGLE_REGEX_STR}$"),
    Switch.check(FunctionType.RESPONDER),
)
async def single_dice_handler(client: Client, group: Group, content: MessageChain):
    faces = int(re.search(SINGLE_REGEX_STR, str(content))[1])
    await send_message(
        client,
        group,
        MessageChain([Text(f"您掷出的点数是:{random.randint(1, faces)}")]),
    )


DND_REGEX_STR = r"\.([1-9]\d{0,2})[Dd][1-9]\d{0,7}"


@listen(GroupMessage)
@decorate(
    MatchRegex(rf"^{DND_REGEX_STR}$"),
    Switch.check(FunctionType.RESPONDER),
)
async def dnd_dice_handler(client: Client, group: Group, content: MessageChain):
    times = int(re.search(DND_REGEX_STR, str(content))[1])
    faces = int(re.search(r"[1-9]\d{0,2}[Dd]([1-9]\d{0,7})", str(content))[1])
    await send_message(
        client,
        group,
        MessageChain(
            [
                Text(
                    "您掷出的点数是:"
                    + " ".join([str(random.randint(1, faces)) for _ in range(times)])
                )
            ]
        ),
    )
