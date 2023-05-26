from typing import overload

from creart import it
from graia.amnesia.message import MessageChain
from graia.broadcast import Broadcast
from ichika.client import Client
from ichika.core import Friend, Group, RawMessageReceipt

from chitung.core.event import ActiveMessage


@overload
async def send_message(
    client: Client, group: Group, content: MessageChain, /
) -> RawMessageReceipt:
    pass


@overload
async def send_message(
    client: Client, friend: Friend, content: MessageChain, /
) -> RawMessageReceipt:
    pass


async def send_message(client, target, content) -> RawMessageReceipt:
    """
    向群组或好友发送消息

    Args:
        client (Client): 客户端实例
        target (Group | Friend): 群组或好友
        content (MessageChain): 消息内容

    Return:
        RawMessageReceipt: 消息回执
    """
    if isinstance(target, Group):
        receipt = await client.send_group_message(target.uin, content)
    elif isinstance(target, Friend):
        receipt = await client.send_friend_message(target.uin, content)
    else:
        raise ValueError("target must be Group or Friend")
    it(Broadcast).postEvent(
        ActiveMessage(client=client, receipt=receipt, content=content)
    )
    return receipt
