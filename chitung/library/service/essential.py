from pathlib import Path

from avilla.core import Avilla
from launart import Launart, Service
from loguru import logger

from chitung.library.const import CHITUNG_ROOT


class ChitungService(Service):
    id = "chitung.service/essential"
    avilla: Avilla

    @property
    def broadcast(self):
        return self.avilla.broadcast

    def __init__(self):
        self.avilla = Avilla()
        super().__init__()

    @property
    def required(self):
        return {
            "chitung.service/config",
            "chitung.service/module",
            "chitung.service/protocol",
        }

    @property
    def stages(self):
        return {"preparing", "cleanup"}

    @staticmethod
    def ensure_path(path: str):
        if not (p := Path(CHITUNG_ROOT, path)).is_dir():
            p.mkdir(parents=True)

    async def launch(self, manager: Launart):
        self.ensure_path("config")
        self.ensure_path("data")
        self.ensure_path("module")
        logger.success("[ChitungService] Ensured all paths")

        async with self.stage("preparing"):
            logger.info("[ChitungService] Current stage: preparing")

        async with self.stage("cleanup"):
            logger.info("[ChitungService] Current stage: cleanup")
