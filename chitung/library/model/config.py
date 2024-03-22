from dataclasses import dataclass, field

from kayaku import config


@dataclass
class ChitungNetworkConfig:
    proxy: str = ""
    timeout: int = 30


@dataclass
class ChitungAdvancedConfig:
    debug: bool = False
    log_rotate: int = 7
    message_cache_size: int = 5000
    uvicorn_port: int = 8000


@config("library.main")
class ChitungConfig:
    name: str = "Chitung"
    description: str = "Yet another bot"
    network: ChitungNetworkConfig = field(default_factory=ChitungNetworkConfig)
    advanced: ChitungAdvancedConfig = field(default_factory=ChitungAdvancedConfig)
