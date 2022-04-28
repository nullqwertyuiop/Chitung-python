from graia.ariadne.event.message import GroupMessage
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from .utils.depends import BlacklistControl

channel = Channel.current()

channel.name("ChitungLottery")
channel.author("角川烈&白门守望者 (Chitung-public)，nullqwertyuiop (Chitung-python)")
channel.description("七筒")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[],
        decorators=[BlacklistControl.enable()],
        priority=7777777
    )
)
async def chitung_priority_controller_handler():
    return
