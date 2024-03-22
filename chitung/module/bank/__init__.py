from avilla.core import Avilla, Context
from avilla.standard.core.message import MessageReceived
from avilla.twilight.twilight import FullMatch, Twilight
from graia.amnesia.message import MessageChain, Text
from graia.saya.builtins.broadcast.shortcut import dispatch, listen

from chitung.library.service.bank import BankService, Currency


@listen(MessageReceived)
@dispatch(Twilight(FullMatch("/bank")))
async def get_bank(avilla: Avilla, ctx: Context):
    vault = avilla.launch_manager.get_component(BankService).vault
    currency = Currency.PUMPKIN_PESO
    balance = await vault.get_balance(ctx.client, currency)
    await ctx.scene.send_message(
        MessageChain([Text(f"您的余额为 {balance} {currency.fullname()}")])
    )
