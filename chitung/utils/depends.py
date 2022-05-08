from typing import NoReturn

from graia.ariadne.event.message import MessageEvent, FriendMessage, GroupMessage
from graia.broadcast import ExecutionStop
from graia.broadcast.builtin.decorators import Depend

from . import config
from .config import group_config
from .models import UserPerm
from ..utils.blacklist import blacklist as bl


class BlacklistControl:
    @staticmethod
    def enable() -> Depend:
        async def blacklist(event: MessageEvent) -> NoReturn:
            if isinstance(event, FriendMessage):
                if event.sender.id in bl.friendBlacklist:
                    raise ExecutionStop
            elif isinstance(event, GroupMessage):
                if (
                    event.sender.group in bl.groupBlacklist
                    or event.sender.id
                    in group_config.get(event.sender.group.id).blockedUser
                ):
                    raise ExecutionStop

        return Depend(blacklist)


class FunctionControl:
    Fish = "fish"
    Casino = "casino"
    Responder = "responder"
    Lottery = "lottery"
    Game = "game"

    @staticmethod
    def enable(function: str) -> Depend:
        async def switch(event: MessageEvent) -> NoReturn:
            if isinstance(event, FriendMessage):
                if any(
                    [not getattr(config.friendFC, function), not config.rc.answerFriend]
                ):
                    raise ExecutionStop
            elif isinstance(event, GroupMessage):
                if any(
                    [
                        not getattr(config.groupFC, function),
                        not config.rc.answerGroup,
                        not group_config.get(event.sender.group.id).globalControl,
                        not getattr(group_config.get(event.sender.group.id), function),
                    ]
                ):
                    raise ExecutionStop

        return Depend(switch)


class Permission:
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
