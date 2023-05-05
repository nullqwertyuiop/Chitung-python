import pkgutil
from pathlib import Path

import kayaku
from creart import it
from graia.broadcast import Broadcast
from graia.saya import Saya
from ichika.graia import IchikaComponent
from ichika.login import PathCredentialStore
from launart import Launart, Launchable
from loguru import logger


class ChitungServiceEssential(Launchable):
    id = "chitung.service/essential"

    def __init__(self):
        self._init_kayaku()
        self._init_ichika()
        self._saya_require()
        super().__init__()

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"preparing", "cleanup"}

    @staticmethod
    def _init_kayaku():
        kayaku.initialize(
            {
                "chitung.nest.{**}": "./config/core.jsonc::{**}",
                "chitung.{**}": "./config/{**}",
            }
        )

        from chitung.core.config import (
            CCConfig,
            ChitungConfig,
            FriendFCConfig,
            GroupFCConfig,
            RCConfig,
        )

        kayaku.create(ChitungConfig)
        kayaku.create(FriendFCConfig)
        kayaku.create(GroupFCConfig)
        kayaku.create(RCConfig)
        kayaku.create(CCConfig)

    @staticmethod
    def _init_ichika():
        from chitung.core._ctx import launch_manager
        from chitung.core.config import ChitungConfig

        mgr = launch_manager.get()
        ick = IchikaComponent(
            PathCredentialStore(Path("config") / "bots"), it(Broadcast)
        )
        account = kayaku.create(ChitungConfig).account
        if len(parts := account.split(":", maxsplit=1)) == 2:
            ick.add_password_login(int(parts[0]), parts[1])
        else:
            ick.add_qrcode_login(int(account))

        mgr.add_launchable(ick)

    @staticmethod
    def _saya_require():
        saya = it(Saya)
        path = Path("chitung") / "module"
        with saya.module_context():
            for module in pkgutil.iter_modules([str(path)]):
                saya.require((path / module.name).as_posix().replace("/", "."))

    async def launch(self, _: Launart):
        async with self.stage("preparing"):
            kayaku.bootstrap()
            kayaku.save_all()
            logger.success("[ChitungService] 已保存配置文件")

        async with self.stage("cleanup"):
            kayaku.save_all()
            logger.success("[ChitungService] 已保存配置文件")
