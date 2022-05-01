import random

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, RegexResult, SpacePolicy, UnionMatch
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from .utils.depends import BlacklistControl

channel = Channel.current()

channel.name("ChitungDice")
channel.author("角川烈&白门守望者 (Chitung-public)，nullqwertyuiop (Chitung-python)")
channel.description("Dice")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    RegexMatch(r"(/[Dd](ice)? ?)|(\.[Dd])").space(SpacePolicy.NOSPACE),
                    RegexMatch(r"[1-9]\d{0,7}") @ "faces"
                ]
            )
        ],
        decorators=[BlacklistControl.enable()]
    )
)
async def chitung_single_dice_handler(
        app: Ariadne,
        event: MessageEvent,
        faces: RegexResult
):
    faces = int(faces.result.asDisplay())
    await app.sendGroupMessage(event.sender.group, MessageChain(f"您掷出的点数是:{random.randint(1, faces)}"))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    RegexMatch(r"\.").space(SpacePolicy.NOSPACE),
                    RegexMatch(r"[1-9]\d{0,2}").space(SpacePolicy.NOSPACE) @ "times",
                    UnionMatch("d", "D").space(SpacePolicy.NOSPACE),
                    RegexMatch(r"[1-9]\d{0,7}") @ "faces"
                ]
            )
        ],
        decorators=[BlacklistControl.enable()]
    )
)
async def chitung_dnd_dice_handler(
        app: Ariadne,
        event: MessageEvent,
        times: RegexResult,
        faces: RegexResult
):
    times = int(times.result.asDisplay())
    faces = int(faces.result.asDisplay())
    await app.sendGroupMessage(
        event.sender.group,
        MessageChain("您掷出的点数是:" + " ".join([str(random.randint(1, faces)) for _ in range(times)]))
    )
