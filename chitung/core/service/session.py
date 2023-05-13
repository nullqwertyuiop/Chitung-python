from creart import add_creator, it
from launart import Launart, Launchable
from loguru import logger

from chitung.core.session import SessionContainer, SessionContainerCreator


class ChitungServiceSession(Launchable):
    id = "chitung.service/session"

    def __init__(self):
        add_creator(SessionContainerCreator)
        super().__init__()

    @property
    def required(self):
        return {"chitung.service/essential"}

    @property
    def stages(self):
        return {"preparing", "cleanup"}

    async def launch(self, _: Launart):
        async with self.stage("preparing"):
            it(SessionContainer).get()
            logger.success(f"[{self.id}] 已初始化 Session 容器")

        async with self.stage("cleanup"):
            await it(SessionContainer).close_all()
            logger.success(f"[{self.id}] 已关闭 Session 容器")
