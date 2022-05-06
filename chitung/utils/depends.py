from typing import NoReturn, Literal

from graia.ariadne.event.message import MessageEvent, FriendMessage, GroupMessage
from graia.broadcast import ExecutionStop, PropagationCancelled
from graia.broadcast.builtin.decorators import Depend

from . import config
from .models import UserPerm
from ..utils.blacklist import blacklist as bl


class BlacklistControl(object):
    @staticmethod
    def enable() -> Depend:
        async def blacklist(event: MessageEvent) -> NoReturn:
            if isinstance(event, FriendMessage):
                if event.sender.id in bl.friendBlacklist:
                    raise ExecutionStop
            elif isinstance(event, GroupMessage):
                if event.sender.group in bl.groupBlacklist:
                    raise ExecutionStop

        return Depend(blacklist)


class FunctionControl(object):
    Fish = "fish"
    Casino = "casino"
    Responder = "responder"
    Lottery = "lottery"
    Game = "game"

    @staticmethod
    def enable(function: str) -> Depend:
        async def switch(event: MessageEvent) -> NoReturn:
            if isinstance(event, FriendMessage):
                if not getattr(config.friendFC, function):
                    raise ExecutionStop
            elif isinstance(event, GroupMessage):
                if not getattr(config.groupFC, function):
                    raise ExecutionStop

        return Depend(switch)


class Permission(object):
    @staticmethod
    def require(permission: UserPerm) -> Depend:
        async def perm_check(event: MessageEvent) -> NoReturn:
            if event.sender.id in config.adminID:
                user_perm = UserPerm.BOT_OWNER
            elif isinstance(event, GroupMessage):
                user_perm = getattr(UserPerm, str(event.sender.permission))
            else:
                user_perm = UserPerm.MEMBER
            if user_perm < permission:
                raise ExecutionStop

        return Depend(perm_check)
