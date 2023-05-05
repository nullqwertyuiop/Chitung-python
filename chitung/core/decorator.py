from enum import Enum
from typing import NoReturn, TypeVar

from graia.broadcast import ExecutionStop
from graia.broadcast.builtin.decorators import Depend
from ichika.graia.event import GroupMessage, MessageEvent
from kayaku import create
from loguru import logger

from chitung.core.config import FriendFCConfig, GroupFCConfig, RCConfig

_T = TypeVar("_T", bound=MessageEvent)


class FunctionType(Enum):
    RESPONDER = "responder"
    CASINO = "casino"
    FISH = "fish"
    LOTTERY = "lottery"
    GAME = "game"


class Switch:
    @classmethod
    def check(
        cls, event_type: type[_T], category: FunctionType, *, show_log: bool = True
    ) -> Depend:
        is_group = event_type == GroupMessage

        async def judge(_: event_type) -> NoReturn:
            # Doesn't support UnionType dispatching yet :(
            try:
                cls._check_rc(is_group)
                cls._check_fc(category, is_group)
            except ExecutionStop as e:
                if show_log:
                    logger.warning(f"[Switch] {category.value} 未开启")
                raise ExecutionStop() from e

        return Depend(judge)

    @staticmethod
    def _check_rc(is_group: bool) -> NoReturn:
        scope = "group" if is_group else "friend"
        rc_config: RCConfig = create(RCConfig)
        if not getattr(rc_config, f"answer_{scope}", False):
            raise ExecutionStop()

    @staticmethod
    def _check_fc(category: FunctionType, is_group: bool) -> NoReturn:
        fc_config = create(GroupFCConfig) if is_group else create(FriendFCConfig)
        if not getattr(fc_config, category.value, False):
            raise ExecutionStop()
