import json

from chitung.utils.models import Config
from pathlib import Path

config_path = Path(Path(__file__).parent.parent) / "data" / "Config.json"


def load_config() -> Config:
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = Config(**json.loads(f.read()))
    return cfg


config = load_config()


def save_config():
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(json.dumps(config.dict(), indent=4, ensure_ascii=False)))


def reload_config():
    global config
    config = load_config()
