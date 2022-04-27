import os.path
from pathlib import Path

from graia.ariadne.event.lifecycle import ApplicationLaunched
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast import ListenerSchema
from loguru import logger

from .utils.blacklist import get_remote_blacklist
from .utils.config import config

saya = Saya.current()
channel = Channel.current()

channel.name("ChitungVanilla")
channel.author("角川烈&白门守望者 (Chitung-public)，nullqwertyuiop (Chitung-python)")
channel.description("七筒")

ignore_list = ["utils", "data", "__init__.py", "__pycache__"]
submodules = [module for module in os.listdir(str(Path(__file__).parent)) if module not in ignore_list]

with saya.module_context():
    for submodule in submodules:
        saya.require(os.path.relpath(Path(Path(__file__).parent) / submodule).replace("\\", ".").replace("/", "."))


@channel.use(ListenerSchema(listening_events=[ApplicationLaunched]))
async def chitung_initialize_handler():
    logger.info("Getting remote blacklist...")
    await get_remote_blacklist()
    if config.botID == 0:
        logger.error("Required field in Config.json: botID")
        exit(0)
