from avilla.core import Context
from avilla.standard.core.message import MessageReceived
from avilla.twilight.twilight import Twilight, FullMatch
from graia.amnesia.message import MessageChain, Text
from graia.saya.builtins.broadcast.shortcut import listen, dispatch


@listen(MessageReceived)
@dispatch(
    Twilight(
        FullMatch("/ping"),
    )
)
async def ping(ctx: Context):
    await ctx.scene.send_message(MessageChain([Text("pong")]))
