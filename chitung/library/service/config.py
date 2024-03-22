import kayaku
from launart import Launart, Service
from loguru import logger


class ConfigService(Service):
    id = "chitung.service/config"

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"preparing", "cleanup"}

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            # TODO: Implement database initialization
            # logger.success("[ConfigService] Initialized database")

            kayaku.bootstrap()
            kayaku.save_all()
            logger.success("[ConfigService] Initialized all configurations")

        async with self.stage("cleanup"):
            kayaku.save_all()
            logger.success("[ConfigService] Saved all configurations")
