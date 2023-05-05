from graia.amnesia.message import MessageChain
from graiax.shortcut import listen, priority
from ichika.client import Client
from ichika.core import Friend, Group, Member
from ichika.graia.event import FriendMessage, GroupMessage, TempMessage
from loguru import logger

ACCOUNT_SEG = "{client.uin}"
GROUP_SEG = "{group.name}({group.uin})"
MEMBER_SEG = "{sender.card_name}({sender.uin})"
FRIEND_SEG = "{sender.nick}({sender.uin})"


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
    logger.info(
        _safe_display(
            seg.format(client=client, group=group, sender=sender, content=content)
        )
    )


@listen(FriendMessage)
@priority(0)
async def log_friend_message(client: Client, sender: Friend, content: MessageChain):
    seg = f"{ACCOUNT_SEG}: [RECV][{FRIEND_SEG}] -> {{content}}"
    logger.info(
        _safe_display(seg.format(client=client, sender=sender, content=content))
    )
