from avilla.core import Context
from avilla.standard.core.message import MessageReceived
from avilla.twilight.twilight import FullMatch, Twilight
from graia.amnesia.message import MessageChain, Text
from graia.broadcast import PropagationCancelled
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast.shortcut import dispatch, listen, priority
from loguru import logger

_saya = Saya.current()


@listen(MessageReceived)
@dispatch(
    Twilight(
        FullMatch("/ping"),
    )
)
async def ping(ctx: Context):
    await ctx.scene.send_message(MessageChain([Text("pong")]))


@listen(MessageReceived)
@priority(0)
async def ignore_self_message(ctx: Context):
    if ctx.client.to_selector() == ctx.self.to_selector():
        logger.debug("ignored self message")
        raise PropagationCancelled()
