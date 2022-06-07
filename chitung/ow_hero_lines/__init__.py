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

channel.name("ChitungOverwatchHerolines")
channel.author("角川烈&白门守望者 (Chitung-public), nullqwertyuiop (Chitung-python)")
channel.description("七筒")

with Path(Path(__file__).parent, "assets", "clusters", "herolines.json").open(
    "r", encoding="utf-8"
) as f:
    clusters = json.loads(f.read())


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    RegexMatch(r"/(大招|英雄不朽)"),
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
        event.sender.group,
        MessageChain(
            random.choice(
                list(random.choice(clusters["ultimateAbilityHeroLines"]).values())[0]
            )
        ),
    )
