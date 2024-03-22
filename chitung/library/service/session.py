from contextlib import suppress
from typing import Set

from aiohttp import ClientSession
from launart import Launart, Service
from launart.status import Phase
from loguru import logger


class SessionService(Service):
    id = "chitung.service/session"

    @property
    def required(self) -> Set[str]:
        return set()

    @property
    def stages(self) -> Set[Phase]:
        return {"preparing", "cleanup"}

    _session: dict[str, ClientSession] = {}

    def get(
        self,
        name: str = "universal",
        flush: bool = False,
        base_url: str = None,
        /,
        **kwargs,
    ) -> ClientSession:
        """
        获取一个 aiohttp.ClientSession 对象

        Args:
            name: 会话名称
            flush: 是否刷新会话
            base_url: 会话的基础 URL，仅会在创建时生效
            **kwargs: 传递给 aiohttp.ClientSession 的参数

        Returns:
            aiohttp.ClientSession 对象
        """
        if flush or name not in self._session or self._session[name].closed:
            self._session[name] = ClientSession(base_url=base_url, **kwargs)
            logger.success(f"[SessionService] Created session {name!r}")
        return self._session[name]

    async def close(self, name: str):
        """
        关闭一个 aiohttp.ClientSession 对象

        Args:
            name: 会话名称
        """
        if name in self._session.copy():
            await self._session[name].close()
            del self._session[name]
            logger.success(f"[SessionService] Closed session {name!r}")

    async def close_all(self):
        """关闭所有 aiohttp.ClientSession 对象，不应被手动调用"""
        for name in self._session.copy():
            with suppress(Exception):
                await self.close(name)

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            self.get()
            logger.success("[SessionService] Default session created")

        async with self.stage("cleanup"):
            await self.close_all()
            logger.success("[SessionService] All sessions closed")
