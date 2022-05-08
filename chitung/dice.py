import random

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.twilight import (
    Twilight,
    RegexMatch,
    RegexResult,
    SpacePolicy,
    UnionMatch,
)
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from .utils.depends import BlacklistControl, FunctionControl


channel = Channel.current()

channel.name("ChitungDice")
channel.author("角川烈&白门守望者 (Chitung-public), nullqwertyuiop (Chitung-python)")
channel.description("Dice")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    RegexMatch(r"(/[Dd](ice)? ?)|(\.[Dd])").space(SpacePolicy.NOSPACE),
                    RegexMatch(r"[1-9]\d{0,7}") @ "faces",
                ]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            FunctionControl.enable("responder"),
        ],
    )
)
async def chitung_single_dice_handler(
    app: Ariadne, event: MessageEvent, faces: RegexResult
):
    faces = int(faces.result.asDisplay())
    await app.sendMessage(
        event.sender.group if isinstance(event, GroupMessage) else event.sender,
        MessageChain(f"您掷出的点数是:{random.randint(1, faces)}"),
    )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[
            Twilight(
                [
                    RegexMatch(r"\.").space(SpacePolicy.NOSPACE),
                    RegexMatch(r"[1-9]\d{0,2}").space(SpacePolicy.NOSPACE) @ "times",
                    UnionMatch("d", "D").space(SpacePolicy.NOSPACE),
                    RegexMatch(r"[1-9]\d{0,7}") @ "faces",
                ]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            FunctionControl.enable(FunctionControl.Responder),
        ],
    )
)
async def chitung_dnd_dice_handler(
    app: Ariadne, event: MessageEvent, times: RegexResult, faces: RegexResult
):
    times = int(times.result.asDisplay())
    faces = int(faces.result.asDisplay())
    await app.sendMessage(
        event.sender.group if isinstance(event, GroupMessage) else event.sender,
        MessageChain(
            "您掷出的点数是:" + " ".join([str(random.randint(1, faces)) for _ in range(times)])
        ),
    )
