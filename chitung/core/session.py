"""
懒得重写了，直接 copy & paste 的 Eric 的 SessionContainer

Source: https://github.com/ProjectNu11/Eric/blob/pdm/library/util/session_container.py
"""
from abc import ABC
from contextlib import suppress

from aiohttp import ClientSession
from creart import AbstractCreator, CreateTargetInfo, exists_module
from loguru import logger


class SessionContainer:
    """会话容器"""

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
            logger.success(f"[SessionContainer] 创建会话 {name!r}")
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
            logger.success(f"[SessionContainer] 已关闭会话 {name!r}")

    async def close_all(self):
        """关闭所有 aiohttp.ClientSession 对象，不应被手动调用"""
        for name in self._session.copy():
            with suppress(Exception):
                await self.close(name)


class SessionContainerCreator(AbstractCreator, ABC):
    targets = (CreateTargetInfo("chitung.core.session", "SessionContainer"),)

    @staticmethod
    def available() -> bool:
        return exists_module("chitung.core.session")

    @staticmethod
    def create(_create_type: type[SessionContainer]) -> SessionContainer:
        return SessionContainer()
