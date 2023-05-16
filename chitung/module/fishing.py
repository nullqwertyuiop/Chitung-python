import asyncio
import json
import random
from asyncio import Lock, TimerHandle
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import TypedDict

from ichika.client import Client
from ichika.core import Friend, Group, Member
from typing_extensions import Self

from chitung.core.service.bank import Currency

ASSETS_PATH = Path("chitung") / "assets" / "fishing"
FISHING_COST = 800
FISHING_CURRENCY = Currency.PUMPKIN_PESO


class Waters(Enum):
    Amur = auto()  # A
    Caroline = auto()  # B
    Chishima = auto()  # C  # noqa
    General = auto()

    @classmethod
    def get(cls, water: str) -> Self:
        water = water.upper()
        if not water:
            return cls.General
        elif water == "A":
            return cls.Amur
        elif water == "B":
            return cls.Caroline
        elif water == "C":
            return cls.Chishima
        return cls.General


class Time(Enum):
    Day = auto()
    Night = auto()
    All = auto()

    @classmethod
    def get(cls, time: str) -> Self:
        time = time.lower()
        if not time:
            return cls.All
        elif time == "day":
            return cls.Day
        elif time == "night":
            return cls.Night
        return cls.All


class Fish(TypedDict):
    code: int
    name: str
    price: int
    time: Time


class SingleRecord(TypedDict):
    ID: int
    recordList: list[int]


class FishHelper:
    flags: dict[int, TimerHandle]
    raw_records: list[datetime]
    fish: list[Fish]
    _write_lock = Lock()

    @property
    def records(self):
        self.raw_records = [
            rec for rec in self.raw_records if rec < datetime.now() - timedelta(hours=1)
        ]
        return self.raw_records

    def load_fish(self):
        with (ASSETS_PATH / "FishingList.json").open("r", encoding="utf-8") as f:
            data = json.loads(f.read())
        fish: list[Fish] = []
        fish.extend(
            {
                "code": item["code"],
                "name": item["name"],
                "price": item["price"],
                "time": Time.get(item["time"]),
            }
            for item in data["fishingList"]
        )
        self.fish = fish

    async def fish_callback(
        self,
        key: int,
        client: Client,
        supplicant: Member | Friend,
        target: Group | Friend,
    ):
        """钓鱼回调"""
        if key not in self.flags.keys():
            return
        self.flags.pop(key)
        # TODO Implement this

    def fish_cancel(self, supplicant: int) -> bool:
        """
        取消钓鱼

        Args:
            supplicant (int): 钓鱼者

        Returns:
            bool: 是否成功取消，若未在钓鱼中则返回 False
        """
        if supplicant not in self.flags.keys():
            return False
        if self.flags[supplicant].cancelled():
            return False
        self.flags[supplicant].cancel()
        return True

    def fish_start(
        self, client: Client, supplicant: Member | Friend, target: Group | Friend
    ) -> bool:
        """
        开始钓鱼

        Args:
            client (Client): 客户端实例
            supplicant (Member | Friend): 钓鱼者
            target (Group | Friend): 钓鱼目标

        Returns:
            bool: 是否成功开始钓鱼，若已在钓鱼中则返回 False
        """
        if supplicant.uin in self.flags.keys():
            return False
        call_delay = 3 + random.randint(0, 3) * len(self.records)
        loop = asyncio.get_running_loop()
        self.flags[supplicant.uin] = loop.call_later(
            call_delay,
            asyncio.create_task,
            self.fish_callback(supplicant.uin, client, supplicant, target),
        )
        return True
