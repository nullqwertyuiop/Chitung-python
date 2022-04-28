import json
import os

from ..utils.models import Config
from pathlib import Path

config_path = Path(Path(__file__).parent.parent) / "data" / "Config.json"

if not os.path.isdir(Path(Path(__file__).parent) / "data"):
    os.mkdir(Path(Path(__file__).parent) / "data")


def load_config() -> Config:
    if os.path.isfile(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = Config(**json.loads(f.read()))
    else:
        cfg = Config()
    return cfg


config = load_config()


def save_config():
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(config.dict(), indent=4, ensure_ascii=False))


save_config()


def reload_config():
    global config
    config = load_config()
