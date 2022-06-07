import json
import random
from pathlib import Path

from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from chitung.utils import BlacklistControl
from chitung.utils.depends import FunctionControl

channel = Channel.current()

channel.name("ChitungAutoReply")
channel.author("角川烈&白门守望者 (Chitung-public), nullqwertyuiop (Chitung-python)")
channel.description("七筒")

with Path(Path(__file__).parent, "assets", "clusters", "autoreply.json").open(
    "r", encoding="utf-8"
) as f:
    clusters = json.loads(f.read())


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    RegexMatch(r"[Hh](i|ello)"),
                ]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            FunctionControl.enable(FunctionControl.Responder),
        ],
    )
)
async def chitung_greeting(app: Ariadne, event: GroupMessage):
    await app.sendGroupMessage(
        event.sender.group, MessageChain(random.choice(["Hi", "Hello", "Hey"]))
    )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    RegexMatch(r".*(下线了|我走了|拜拜).*"),
                ]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            FunctionControl.enable(FunctionControl.Responder),
        ],
    )
)
async def chitung_goodbye(app: Ariadne, event: GroupMessage):
    await app.sendGroupMessage(
        event.sender.group,
        MessageChain(random.choice(list(clusters["goodbyeReplyLines"].values()))),
    )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    RegexMatch(r".*(([Oo])verwatch|守望((先锋)|(屁股))|([玩打])((OW)|(ow))).*"),
                ]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            FunctionControl.enable(FunctionControl.Responder),
        ],
    )
)
async def chitung_anti_ow(app: Ariadne, event: GroupMessage):
    await app.sendGroupMessage(
        event.sender.group,
        MessageChain(
            random.choice(list(clusters["antiOverwatchGameReplyLines"].values()))
        ),
    )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    RegexMatch(
                        r".*(([日干操艹草滚])([你尼泥])([妈马麻])|"
                        r"([Mm])otherfucker|([Ff])uck).*"
                    ),
                ]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            FunctionControl.enable(FunctionControl.Responder),
        ],
    )
)
async def chitung_anti_dirty_words(app: Ariadne, event: GroupMessage):
    await app.sendGroupMessage(
        event.sender.group,
        MessageChain(
            random.choice(list(clusters["antiDirtyWordsReplyLines"].values()))
        ),
    )
