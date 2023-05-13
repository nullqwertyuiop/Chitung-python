import json
from enum import Enum
from pathlib import Path
from typing import NoReturn

from graia.amnesia.message import MessageChain, Text
from ichika.core import Friend, Member
from ichika.message.elements import At
from launart import Launart, Launchable
from loguru import logger

DATA_PATH = Path("data")
VAULT_PATH = Path(DATA_PATH / "bank_record.json")


class Currency(Enum):
    """货币类型"""

    PUMPKIN_PESO = ("pk", "南瓜比索")
    AKAONI = ("ak", "赤鬼金币")  # noqa
    ANTONINIANUS = ("an", "安东尼银币")  # noqa
    ADVENTURER_S = ("ad", "冒险家铜币")
    DEFAULT = PUMPKIN_PESO


class SimpleVault:
    vault: dict[str, dict]

    def __init__(self):
        if not VAULT_PATH.is_file():
            self.vault = {}
            self.store_bank()
        else:
            self.load_bank()

    def get_bank_msg(
        self,
        sender: Member | Friend,
        c_list: list[Currency] = None,
        is_group: bool = True,
    ) -> MessageChain:
        """
        依据传入的 `member` 与 `c_list` 生成包含特定用户就某货币类型余额信息的消息链

        Args:
            :param sender: 需要获取余额的用户
            :param c_list: 需要获取余额的货币类型，可同时传入多种货币类型，默认为 Currency.DEFAULT
            :param is_group: 消息链目标是否未群组，默认为 True

        Returns:
            MessageChain: 包含用户余额信息的消息链
        """

        c_list = c_list or [Currency.DEFAULT]

        user_bank = self.get_bank(sender, c_list, chs=True)
        msg_chain = (
            [At(target=sender.uin, display=sender.card_name), Text(text=" ")]
            if is_group
            else []
        ) + [Text(text="您的余额为")]
        return MessageChain(
            msg_chain
            + [Text(text=f" {value} {key}") for key, value in user_bank.items()]
        )

    def get_bank(
        self,
        sender: Member | Friend,
        c_list: list[Currency] = None,
        *,
        chs: bool = False,
    ) -> dict[str, int]:
        """
        依据传入的 `member` 与 `c_list` 获取特定用户就某货币类型的余额

        Args:
            :param sender: 需要获取余额的用户
            :param c_list: 需要获取余额的货币类型，可同时传入多种货币类型，默认为 Currency.DEFAULT
            :param chs: 返回字典 key 是否为中文，默认为 False

        Returns:
            dict[str, int]: 包含用户余额信息的字典
        """

        c_list = c_list or [Currency.DEFAULT]

        if str(sender.uin) in self.vault.keys():
            return {
                c.value[1 if chs else 0]: int(
                    self.vault[str(sender.uin)].get(c.value[0])
                )
                for c in c_list
            }

        for c in c_list:
            self.set_bank(sender.uin, 0, c)
        return self.get_bank(sender, c_list, chs=chs)

    def store_bank(self) -> NoReturn:
        VAULT_PATH.parent.mkdir(parents=True, exist_ok=True)
        """写入 vault 至 json"""
        with VAULT_PATH.open("w", encoding="utf-8") as f:
            f.write(json.dumps(self.vault, indent=4))

    def load_bank(self) -> NoReturn:
        """读取 json 至 vault"""
        with VAULT_PATH.open("r", encoding="utf-8") as f:
            self.vault = json.loads(f.read())

    def update_bank(
        self, supplicant: int, amount: int, c: Currency = Currency.DEFAULT
    ) -> int:
        """
        依据传入的 `supplicant`, `amount` 与 `c` 更新特定用户就某货币类型的余额

        Args:
            :param supplicant: 余额变动的用户
            :param amount: 变动的金额
            :param c: 变动金额的货币类型，默认为 Currency.DEFAULT

        Returns:
            int: 变动后的金额
        """
        if str(supplicant) in self.vault.keys():
            self.vault[str(supplicant)][c.value[0]] += amount
        else:
            self.vault[str(supplicant)] = {[c.value[0]]: amount}
        self.store_bank()
        return self.vault[str(supplicant)][c.value[0]]

    def set_bank(
        self, supplicant: int, amount: int, c: Currency = Currency.DEFAULT
    ) -> int:
        """
        依据传入的 `supplicant`, `amount` 与 `c` 设置特定用户就某货币类型的余额

        Args:
            :param supplicant: 设置余额的用户
            :param amount: 设置的金额
            :param c: 设置金额的货币类型，默认为 Currency.DEFAULT

        Returns:
            int: 设置后的金额
        """
        if str(supplicant) in self.vault.keys():
            self.vault[str(supplicant)][c.value[0]] = amount
        else:
            self.vault[str(supplicant)] = {c.value[0]: amount}
        self.store_bank()
        return self.vault[str(supplicant)][c.value[0]]

    def has_enough_money(
        self, sender: Member | Friend, amount: int, c: Currency = Currency.DEFAULT
    ) -> bool:
        """
        依据传入的 `supplicant`, `amount` 与 `c` 检查特定用户是否有某货币类型的足够余额

        Args:
            :param sender: 检查的用户
            :param amount: 检查的金额
            :param c: 检查金额的货币类型，默认为 Currency.DEFAULT

        Returns:
            bool: 是否有足够余额
        """
        if str(sender.uin) in self.vault.keys():
            return self.vault[str(sender.uin)].get(c.value[0]) >= amount
        else:
            return False


vault = SimpleVault()


class ChitungServiceBank(Launchable):
    id = "chitung.service/bank"

    @property
    def required(self):
        return {"chitung.service/essential"}

    @property
    def stages(self):
        return {"cleanup"}

    async def launch(self, _: Launart):
        async with self.stage("cleanup"):
            vault.store_bank()
            logger.success(f"[{self.id}] 已保存银行数据")
