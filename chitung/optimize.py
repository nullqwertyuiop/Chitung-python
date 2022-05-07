from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage, FriendMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.twilight import Twilight, FullMatch
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from chitung.utils.depends import Permission
from chitung.utils.models import UserPerm
from chitung.utils.priority import init_priority

channel = Channel.current()

channel.name("ChitungOptimize")
channel.author("角川烈&白门守望者 (Chitung-public), nullqwertyuiop (Chitung-python)")
channel.description("七筒")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[Twilight([FullMatch("/optimize")])],
        decorators=[Permission.require(UserPerm.BOT_OWNER)],
    )
)
async def chitung_optimize_handler(app: Ariadne, event: MessageEvent):
    init_priority()
    await app.sendMessage(
        event.sender.group if isinstance(event, GroupMessage) else event.sender,
        MessageChain("<! Placeholder !>"),
    )
