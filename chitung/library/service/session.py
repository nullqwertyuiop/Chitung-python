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
        if flush or name not in self._session or self._session[name].closed:
            self._session[name] = ClientSession(base_url=base_url, **kwargs)
            logger.success(f"[SessionService] Created session {name!r}")
        return self._session[name]

    async def close(self, name: str):
        if name in self._session.copy():
            await self._session[name].close()
            del self._session[name]
            logger.success(f"[SessionService] Closed session {name!r}")

    async def close_all(self):
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
