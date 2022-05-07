import os.path
from pathlib import Path

from graia.saya import Saya, Channel

saya = Saya.current()
channel = Channel.current()

channel.name("ChitungVanilla")
channel.author("角川烈&白门守望者 (Chitung-public), nullqwertyuiop (Chitung-python)")
channel.description("七筒")

ignore_list = ["data", "__init__.py", "__pycache__"]
submodules = [
    module.split(".")[0]
    for module in os.listdir(str(Path(__file__).parent))
    if module not in ignore_list
]

with saya.module_context():
    for submodule in submodules:
        saya.require(
            os.path.relpath(Path(Path(__file__).parent) / submodule)
            .replace("\\", ".")
            .replace("/", ".")
        )
