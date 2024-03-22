import json
import os
from pathlib import Path
from typing import Final

from avilla.console.protocol import ConsoleProtocol
from avilla.core import BaseProtocol
from launart import Launart, Service
from loguru import logger

from chitung.library.model.protocol import ProtocolConfig
from chitung.library.service import ChitungService
from chitung.library.const import CHITUNG_ROOT

_PROTOCOL_CREDENTIAL_PATH: Final[Path] = Path(
    CHITUNG_ROOT, "config", "library", "credentials"
)


class ProtocolService(Service):
    id = "chitung.service/protocol"

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"preparing"}

    def _load_console(self):
        if os.environ.get("CHITUNG_NO_CONSOLE") != "1":
            self.apply_protocols(ConsoleProtocol())
        else:
            logger.warning("[ProtocolService] Console protocol disabled")

    def apply_protocols(self, *protocols: BaseProtocol):
        self.manager.get_component(ChitungService).avilla.apply_protocols(*protocols)

    def _load_protocols(self):
        configs: list[ProtocolConfig] = []
        for file in _PROTOCOL_CREDENTIAL_PATH.rglob("*.json"):
            with file.open("r") as f:
                protocol = ProtocolConfig.resolve(json.load(f))
                if protocol.enabled:
                    configs.append(protocol)
        if not configs:
            return
        logger.success(f"[ProtocolService] Loaded {len(configs)} registered protocols")
        self.apply_protocols(*(config.to_protocol() for config in configs))

    def register_protocol(self, config: ProtocolConfig):
        protocol_dir = _PROTOCOL_CREDENTIAL_PATH / config.protocol
        if not protocol_dir.exists():
            protocol_dir.mkdir(parents=True)
        with (protocol_dir / f"{config.id}.json").open("w") as f:
            f.write(config.model_dump_json(indent=4))
        self.apply_protocols(config.to_protocol())

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            self._load_console()
            self._load_protocols()
