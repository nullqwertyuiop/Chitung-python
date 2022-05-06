import json
import os
import os.path
from enum import Enum
from pathlib import Path
from typing import List, Dict, NoReturn

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain
from graia.ariadne.message.parser.twilight import Twilight, FullMatch, RegexMatch, RegexResult
from graia.ariadne.model import Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from .utils.depends import BlacklistControl, FunctionControl, Permission
from .utils.models import UserPerm

channel = Channel.current()

channel.name("ChitungBank")
channel.author("角川烈&白门守望者 (Chitung-public), nullqwertyuiop (Chitung-python)")
channel.description("/bank")

data_dir = Path(Path(__file__).parent / "data")
vault_dir = Path(data_dir / "bank_record.json")


class Currency(Enum):
    """ 货币类型，记得用 CUCUMBER_PESO """

    CUCUMBER_PESO = ("cp", "黄瓜比索")
    PUMPKIN_PESO = ("pk", "南瓜比索")
    AKAONI = ("ak", "赤鬼金币")
    ANTONINIANUS = ("an", "安东尼银币")
    ADVENTURER_S = ("ad", "冒险家铜币")

    DEFAULT = ("cp", "黄瓜比索")


class Vault:
    vault: Dict[str, Dict]

    def __init__(self):
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)
        if not os.path.exists(vault_dir):
            self.vault = {}
            self.store_bank()
        else:
            self.load_bank()

    def get_bank_msg(
            self,
            member: Member,
            c_list: List[Currency] = None,
            is_group: bool = True
    ) -> MessageChain:
        """
        依据传入的 `member` 与 `c_list` 生成包含特定用户就某货币类型余额信息的消息链

        Args:
            :param member: 需要获取余额的用户
            :param c_list: 需要获取余额的货币类型，可同时传入多种货币类型，默认为 Currency.DEFAULT
            :param is_group: 消息链目标是否未群组，默认为 True

        Returns:
            MessageChain: 包含用户余额信息的消息链
        """

        if c_list is None:
            c_list = [Currency.DEFAULT]

        user_bank = self.get_bank(member, c_list, chs=True)
        msg_chain = ([At(member), Plain(text=" ")] if is_group else []) + [Plain(text="您的余额为")]
        return MessageChain.create(
            msg_chain + [Plain(text=f" {value} {key}") for key, value in user_bank.items()]
        )

    def get_bank(
            self,
            member: Member,
            c_list: List[Currency] = None,
            *,
            chs: bool = False
    ) -> Dict[str, int]:
        """
        依据传入的 `member` 与 `c_list` 获取特定用户就某货币类型的余额

        Args:
            :param member: 需要获取余额的用户
            :param c_list: 需要获取余额的货币类型，可同时传入多种货币类型，默认为 Currency.DEFAULT
            :param chs: 返回字典 key 是否为中文，默认为 False

        Returns:
            Dict[str, int]: 包含用户余额信息的字典
        """

        if not c_list:
            c_list = [Currency.DEFAULT]

        if str(member.id) in self.vault.keys():
            user_bank = {c.value[0 if not chs else 1]: int(self.vault[str(member.id)].get(c.value[0])) for c in c_list}
        else:
            for c in c_list:
                self.set_bank(member.id, 0, c)
            user_bank = self.get_bank(member, c_list, chs=chs)
        return user_bank

    def store_bank(self) -> NoReturn:
        """ 写入 vault 至 json """
        with open(vault_dir, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.vault, indent=4))

    def load_bank(self) -> NoReturn:
        """ 读取 json 至 vault """
        with open(vault_dir, "r", encoding="utf-8") as f:
            self.vault = json.loads(f.read())

    def update_bank(
            self,
            supplicant: int,
            amount: int,
            c: Currency = Currency.DEFAULT
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
            self,
            supplicant: int,
            amount: int,
            c: Currency = Currency.DEFAULT
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
            self,
            supplicant: Member,
            amount: int,
            c: Currency = Currency.DEFAULT
    ) -> bool:
        """
        依据传入的 `supplicant`, `amount` 与 `c` 检查特定用户是否有某货币类型的足够余额

        Args:
            :param supplicant: 检查的用户
            :param amount: 检查的金额
            :param c: 检查金额的货币类型，默认为 Currency.DEFAULT

        Returns:
            bool: 是否有足够余额
        """
        if str(supplicant.id) in self.vault.keys():
            return self.vault[str(supplicant.id)].get(c.value[0]) >= amount
        else:
            return False


vault = Vault()


@channel.use(
    ListenerSchema(
        listening_events=[
            GroupMessage,
            FriendMessage
        ],
        inline_dispatchers=[
            Twilight(
                [
                    FullMatch("/bank")
                ]
            )
        ],
        decorators=[
            Permission.require(UserPerm.OWNER),
            BlacklistControl.enable(),
            FunctionControl.enable(FunctionControl.Casino)
        ]
    )
)
async def chitung_bank_handler(
        app: Ariadne,
        event: MessageEvent
):
    await app.sendMessage(
        event.sender.group
        if isinstance(event, GroupMessage)
        else event.sender,
        vault.get_bank_msg(
            event.sender,
            [Currency.CUCUMBER_PESO],
            is_group=True
            if isinstance(event, GroupMessage)
            else False
        )
    )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    FullMatch("/set"),
                    RegexMatch(r"\d+ ") @ "target",
                    RegexMatch(r"\d+") @ "amount"
                ]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            FunctionControl.enable(FunctionControl.Casino),
            Permission.require(UserPerm.BOT_OWNER)
        ]
    )
)
async def chitung_bank_set_handler(
        app: Ariadne,
        event: MessageEvent,
        target: RegexResult,
        amount: RegexResult
):
    target = int(target.result.asDisplay().strip())
    amount = int(amount.result.asDisplay())
    vault.set_bank(
        target,
        amount,
        Currency.CUCUMBER_PESO
    )
    await app.sendMessage(
        event.sender.group
        if isinstance(event, GroupMessage)
        else event.sender,
        MessageChain("已设置成功。")
    )


@channel.use(
    ListenerSchema(
        listening_events=[
            GroupMessage,
            FriendMessage
        ],
        inline_dispatchers=[
            Twilight(
                [
                    FullMatch("/laundry"),
                    RegexMatch(r"\d+") @ "amount"
                ]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            FunctionControl.enable(FunctionControl.Casino),
            Permission.require(UserPerm.BOT_OWNER)
        ]
    )
)
async def chitung_bank_laundry_handler(
        event: MessageEvent,
        amount: RegexResult
):
    amount = int(amount.result.asDisplay())
    vault.update_bank(
        event.sender.id,
        amount,
        Currency.CUCUMBER_PESO
    )
