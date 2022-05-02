from typing import NoReturn, Literal

from graia.ariadne.event.message import MessageEvent, FriendMessage, GroupMessage
from graia.broadcast import ExecutionStop
from graia.broadcast.builtin.decorators import Depend

from . import config
from ..utils.blacklist import blacklist as bl


class BlacklistControl(object):
    @staticmethod
    def enable() -> Depend:
        async def blacklist(event: MessageEvent) -> NoReturn:
            if isinstance(event, FriendMessage):
                if event.sender.id in bl.friendBlacklist:
                    raise ExecutionStop()
            elif isinstance(event, GroupMessage):
                if event.sender.group in bl.groupBlacklist:
                    raise ExecutionStop()

        return Depend(blacklist)


class FunctionControl(object):
    @staticmethod
    def enable(function: Literal['fish', 'casino', 'responder', 'lottery', 'game']) -> Depend:
        async def switch(event: MessageEvent) -> NoReturn:
            if isinstance(event, FriendMessage):
                if not getattr(config.friendFC, function):
                    raise ExecutionStop()
            elif isinstance(event, GroupMessage):
                if not getattr(config.groupFC, function):
                    raise ExecutionStop()

        return Depend(switch)
