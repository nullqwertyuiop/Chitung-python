import asyncio
from asyncio import Lock
from datetime import datetime, timedelta
from enum import Enum, auto
from heapq import heapify, heappop, heappush

from graia.amnesia.transport.common.storage import CacheStorage
from launart import Launart, Service
from loguru import logger


class FieldType(Enum):
    GROUP = auto()
    USER = auto()


class MPSEType(Enum):
    DAILY = 4500
    HALF_DAY = 2500
    SIX_HOUR = 1500
    THREE_HOUR = 1000
    ONE_HOUR = 500


_lock = Lock()


def _with_lock(func):
    async def wrapper(*args, **kwargs):
        async with _lock:
            return await func(*args, **kwargs)

    return wrapper


class MPSECache(CacheStorage[datetime]):
    cache: dict[FieldType, list[datetime]]
    expire: list[tuple[datetime, FieldType]]

    def __init__(
        self,
        cache: dict[FieldType, list[datetime]],
        expire: list[tuple[datetime, FieldType]],
    ):
        self.cache = cache
        self.expire = expire

    @_with_lock
    async def get(self, key: FieldType, _: int = None) -> int:
        return len(self.cache[key])

    @_with_lock
    async def set(
        self,
        key: FieldType,
        value: datetime | None = None,
        expire: timedelta | None = timedelta(days=1),
    ) -> None:
        value = value or datetime.now()
        expire = expire or timedelta(0)
        value = value + expire
        heappush(self.expire, (value, key))
        heappush(self.cache[key], value)

    async def add(self, key: FieldType):
        """Add a new record to the cache."""
        await self.set(key, datetime.now())

    async def filter(self, field: FieldType, typ: MPSEType) -> int:
        """Filter the cache by type."""
        data = self.cache[field]
        match typ:
            case MPSEType.DAILY:
                return len(data)
            case MPSEType.HALF_DAY:
                return len(
                    [i for i in data if i > datetime.now() + timedelta(hours=12)]
                )
            case MPSEType.SIX_HOUR:
                return len(
                    [i for i in data if i > datetime.now() + timedelta(hours=18)]
                )
            case MPSEType.THREE_HOUR:
                return len(
                    [i for i in data if i > datetime.now() + timedelta(hours=21)]
                )
            case MPSEType.ONE_HOUR:
                return len(
                    [i for i in data if i > datetime.now() + timedelta(hours=23)]
                )
            case _:
                return 0

    async def batch_filter(
        self, field: FieldType, *types: MPSEType
    ) -> dict[MPSEType, int]:
        """Filter the cache by multiple types."""
        return {typ: await self.filter(field, typ) for typ in types}

    @_with_lock
    async def delete(self, key: FieldType, strict: bool = False) -> None:
        if strict or key in self.cache:
            self.cache[key] = []

    @_with_lock
    async def clear(self) -> None:
        self.cache = {FieldType.GROUP: [], FieldType.USER: []}
        self.expire.clear()

    @_with_lock
    async def has(self, key: FieldType) -> bool:
        return key in self.cache

    @_with_lock
    async def keys(self) -> list[FieldType]:
        return list(self.cache.keys())


class MPSEService(Service):
    id = "chitung.service/mpse"
    supported_interface_types = {MPSECache}

    interval: float
    cache: dict[FieldType, list[datetime]]
    expire: list[tuple[datetime, FieldType]]

    def __init__(
        self,
        interval: float = 0.1,
        cache: dict[int, list[tuple[float, int, int]]] = None,
        expire: list[tuple[float, int]] = None,
    ):
        self.interval = interval
        self.cache = cache or {FieldType.GROUP: [], FieldType.USER: []}
        self.expire = expire or []
        heapify(self.expire)
        for key in self.cache.keys():
            heapify(self.cache[key])
        super().__init__()

    @property
    def required(self):
        return {"chitung.service/essential"}

    def get_interface(self, _) -> MPSECache:
        # 只能传入 reference，否则会导致清理失败
        return MPSECache(self.cache, self.expire)

    @property
    def stages(self):
        return {"blocking"}

    async def launch(self, manager: Launart) -> None:
        async with self.stage("blocking"):
            logger.success(f"[{self.id}] MPSE 服务已启动")
            while not manager.status.exiting:
                while self.expire and self.expire[0][0] <= datetime.now():
                    async with _lock:
                        _, key = heappop(self.expire)
                        heappop(self.cache[key])
                await asyncio.sleep(self.interval)
            logger.success(f"[{self.id}] MPSE 服务已停止")
