from graia.amnesia.message import MessageChain
from graiax.shortcut import listen, priority
from ichika.client import Client
from ichika.core import Friend, Group, Member, RawMessageReceipt
from ichika.graia.event import FriendMessage, GroupMessage, TempMessage
from loguru import logger

from chitung.core.event import ActiveMessage

ACCOUNT_SEG = "{client.uin}"
GROUP_SEG = "{group.name}({group.uin})"
MEMBER_SEG = "{name}({sender.uin})"
FRIEND_SEG = "{sender.nick}({sender.uin})"
RECEIPT_FRIEND_SEG = "{sender.nickname}({sender.uin})"


def _safe_display(content: str) -> str:
    return repr(content)[1:-1]


@listen(GroupMessage, TempMessage)
@priority(0)
async def log_group_message(
    client: Client,
    group: Group,
    sender: Member,
    content: MessageChain,
):
    seg = f"{ACCOUNT_SEG}: [RECV][{GROUP_SEG}] {MEMBER_SEG} -> {{content}}"
    name = sender.card_name or sender.nickname
    logger.info(
        _safe_display(
            seg.format(
                client=client, group=group, name=name, sender=sender, content=content
            )
        )
    )


@listen(FriendMessage)
@priority(0)
async def log_friend_message(client: Client, sender: Friend, content: MessageChain):
    seg = f"{ACCOUNT_SEG}: [RECV][{FRIEND_SEG}] -> {{content}}"
    logger.info(
        _safe_display(seg.format(client=client, sender=sender, content=content))
    )


@listen(ActiveMessage)
@priority(0)
async def log_active_message(
    client: Client, receipt: RawMessageReceipt, content: MessageChain
):
    if receipt.kind == "group":
        group = await client.get_group(receipt.target)
        seg = f"{ACCOUNT_SEG}: [SEND][{GROUP_SEG}] <- {content}"
        logger.info(
            _safe_display(seg.format(client=client, group=group, content=content))
        )
    elif receipt.kind == "friend":
        friend = await client.get_profile(receipt.target)
        seg = f"{ACCOUNT_SEG}: [SEND][{RECEIPT_FRIEND_SEG}] <- {content}"
        logger.info(
            _safe_display(seg.format(client=client, sender=friend, content=content))
        )
