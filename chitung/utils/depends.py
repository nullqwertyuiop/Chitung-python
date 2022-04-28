from typing import NoReturn

from graia.ariadne.event.message import MessageEvent, FriendMessage, GroupMessage
from graia.broadcast import ExecutionStop
from graia.broadcast.builtin.decorators import Depend

from .config import config
from ..utils.blacklist import blacklist as bl


class BlacklistControl(object):
    @staticmethod
    def enable() -> Depend:
        async def blacklist(event: MessageEvent) -> NoReturn:
            if config.loadRemoteBlacklist and event.sender.id in bl.remoteBlacklist:
                raise ExecutionStop()
            if isinstance(event, FriendMessage):
                if event.sender.id in bl.friendBlacklist:
                    raise ExecutionStop()
            elif isinstance(event, GroupMessage):
                if event.sender.group in bl.groupBlacklist:
                    raise ExecutionStop()

        return Depend(blacklist)
