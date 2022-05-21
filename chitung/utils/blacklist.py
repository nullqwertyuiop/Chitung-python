import json
import os
from pathlib import Path
from typing import Literal

from ..utils.models import BlacklistModel

if not os.path.isdir(Path(Path(__file__).parent.parent) / "data"):
    os.mkdir(Path(Path(__file__).parent.parent) / "data")


def load_blacklist() -> BlacklistModel:
    if os.path.isfile(Path(Path(__file__).parent.parent) / "data" / "Blacklist.json"):
        with open(
            Path(Path(__file__).parent.parent) / "data" / "Blacklist.json",
            "r",
            encoding="utf-8",
        ) as f:
            bl = BlacklistModel(**json.loads(f.read()))
    else:
        bl = BlacklistModel()
    return bl


def store_blacklist():
    with open(
        Path(Path(__file__).parent.parent) / "data" / "Blacklist.json",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(json.dumps(blacklist.dict(), indent=4, ensure_ascii=False))


blacklist: BlacklistModel = load_blacklist()
store_blacklist()


def add_blacklist(target_id: int, target_type: Literal["friend", "group"]) -> bool:
    if target_type == "friend":
        if target_id in blacklist.friendBlacklist:
            return False
        blacklist.friendBlacklist.append(target_id)
    elif target_id in blacklist.groupBlacklist:
        return False
    else:
        blacklist.groupBlacklist.append(target_id)
    store_blacklist()
    return True


def remove_blacklist(target_id: int, target_type: Literal["friend", "group"]):
    if target_type == "friend":
        if target_id not in blacklist.friendBlacklist:
            return False
        blacklist.friendBlacklist.remove(target_id)
    elif target_id in blacklist.groupBlacklist:
        blacklist.groupBlacklist.remove(target_id)
    else:
        return False
    store_blacklist()
    return True
