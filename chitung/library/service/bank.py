from asyncio import Lock
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Final

from avilla.core import Selector
from launart import Launart, Service
from loguru import logger
from pydantic import BaseModel

from chitung.library.const import DATA_ROOT

DATA_PATH: Final[Path] = DATA_ROOT / "bank_record.json"


class CurrencyFullName(str, Enum):
    PUMPKIN_PESO = "南瓜比索"
    AKAONI = "赤鬼金币"
    ANTONINIANUS = "安东尼银币"
    ADVENTURER_S = "冒险家铜币"

    def shortname(self) -> "Currency":
        return Currency[self.name]


class Currency(str, Enum):
    PUMPKIN_PESO = "pk"
    AKAONI = "ak"
    ANTONINIANUS = "an"
    ADVENTURER_S = "ad"

    def fullname(self) -> "CurrencyFullName":
        return CurrencyFullName[self.name]


class VaultAccount(BaseModel):
    balance: dict[Currency, int]

    def deposit(self, currency: Currency, amount: int):
        self.balance[currency] += amount

    def withdraw(self, currency: Currency, amount: int):
        self.balance[currency] -= amount

    def get_balance(self, currency: Currency) -> int:
        return self.balance.setdefault(currency, 0)

    def set_balance(self, currency: Currency, amount: int):
        self.balance[currency] = amount

    def has_enough(self, currency: Currency, amount: int) -> bool:
        return self.get_balance(currency) >= amount


class VaultLand(BaseModel):
    accounts: dict[str, VaultAccount]

    def get_account(self, target: Selector) -> VaultAccount:
        return self.accounts.setdefault(
            target.last_value,
            VaultAccount(balance={currency: 0 for currency in Currency}),
        )


class SimpleVault(BaseModel):
    vault: dict[str, VaultLand]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__lock: dict[Selector, Lock] = {}

    @asynccontextmanager
    async def _lock(self, target: Selector):
        async with self.__lock.setdefault(target, Lock()):
            yield

    def get_land(self, target: Selector) -> VaultLand:
        return self.vault.setdefault(target.pattern["land"], VaultLand(accounts={}))

    def get_account(self, target: Selector) -> VaultAccount:
        return self.get_land(target).get_account(target)

    async def deposit(self, target: Selector, currency: Currency, amount: int):
        async with self._lock(target):
            self.get_account(target).deposit(currency, amount)

    async def withdraw(self, target: Selector, currency: Currency, amount: int):
        async with self._lock(target):
            self.get_account(target).withdraw(currency, amount)

    async def get_balance(self, target: Selector, currency: Currency) -> int:
        async with self._lock(target):
            return self.get_account(target).get_balance(currency)

    async def set_balance(self, target: Selector, currency: Currency, amount: int):
        async with self._lock(target):
            self.get_account(target).set_balance(currency, amount)

    async def has_enough(
        self, target: Selector, currency: Currency, amount: int
    ) -> bool:
        async with self._lock(target):
            return self.get_account(target).has_enough(currency, amount)


class BankService(Service):
    id = "chitung.service/bank"
    vault: SimpleVault

    @property
    def required(self):
        return {"chitung.service/essential"}

    @property
    def stages(self):
        return {"preparing", "cleanup"}

    async def launch(self, _: Launart):
        async with self.stage("preparing"):
            try:
                if DATA_PATH.is_file():
                    self.vault = SimpleVault.model_validate_json(DATA_PATH.read_text())
                else:
                    logger.warning("bank data not found, loading empty vault")
                    self.vault = SimpleVault(vault={})
            except Exception as err:
                logger.error(f"failed to load bank data: {err}")
                bak = DATA_PATH.rename(
                    DATA_PATH.with_suffix(
                        f"{datetime.now(timezone.utc).timestamp()}.bak"
                    )
                )
                logger.warning(f"backup bank data to {bak}")
                self.vault = SimpleVault(vault={})

        async with self.stage("cleanup"):
            DATA_PATH.write_text(self.vault.model_dump_json(include={"vault"}))
            logger.success(f"[{self.id}] saved bank data to {DATA_PATH}")
