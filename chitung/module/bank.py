import re

from graia.amnesia.message import MessageChain, Text
from graiax.shortcut import decorate, listen
from graiax.shortcut.text_parser import MatchRegex
from ichika.client import Client
from ichika.core import Friend, Group, Member
from ichika.graia.event import FriendMessage, GroupMessage

from chitung.core.decorator import FunctionType, Permission, Switch
from chitung.core.service.bank import Currency, vault
from chitung.core.util import send_message

SET_PATTERN = r"^/set (\d+) (\d+)$"
LAUNDRY_PATTERN = r"^/laundry (\d+)$"


@listen(GroupMessage)
@decorate(
    MatchRegex(r"^/bank$"),
    Switch.check(FunctionType.CASINO),
)
async def group_bank_handler(client: Client, member: Member, group: Group):
    await send_message(
        client,
        group,
        vault.get_bank_msg(
            member,
            [Currency.PUMPKIN_PESO],
            is_group=True,
        ),
    )


@listen(FriendMessage)
@decorate(
    MatchRegex(r"^/bank$"),
    Switch.check(FunctionType.CASINO),
)
async def friend_bank_handler(client: Client, friend: Friend):
    await send_message(
        client,
        friend,
        vault.get_bank_msg(
            friend,
            [Currency.PUMPKIN_PESO],
            is_group=True,
        ),
    )


@listen(GroupMessage, FriendMessage)
@decorate(
    MatchRegex(SET_PATTERN),
    Switch.check(FunctionType.CASINO),
    Permission.owner(),
)
async def group_bank_set_handler(
    client: Client, content: MessageChain, target: Group | Friend
):
    supplicant = int(re.match(SET_PATTERN, str(content))[1])
    amount = int(re.match(SET_PATTERN, str(content))[2])
    vault.set_bank(supplicant, amount, Currency.PUMPKIN_PESO)
    await send_message(client, target, MessageChain([Text("已设置成功。")]))


@listen(GroupMessage, FriendMessage)
@decorate(
    MatchRegex(LAUNDRY_PATTERN),
    Switch.check(FunctionType.CASINO),
    Permission.owner(),
)
async def bank_laundry_handler(sender: Member | Friend, content: MessageChain):
    amount = int(re.match(LAUNDRY_PATTERN, str(content))[1])
    vault.update_bank(sender.uin, amount, Currency.PUMPKIN_PESO)
