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
            logger.success("[ChitungService] 已保存配置文件")

        async with self.stage("cleanup"):
            await it(SessionContainer).close_all()
            logger.success("[ChitungService] 已保存配置文件")
