import json
import os
import os.path
from enum import Enum
from pathlib import Path
from typing import Union, List, Dict, NoReturn

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain
from graia.ariadne.message.parser.twilight import Twilight, FullMatch, RegexMatch, RegexResult
from graia.ariadne.model import Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from ..utils.config import config
from ..utils.depends import BlacklistControl

channel = Channel.current()

channel.name("ChitungBank")
channel.author("角川烈&白门守望者 (Chitung-public)，nullqwertyuiop (Chitung-python)")
channel.description("/bank")

data_dir = Path(Path(__file__).parent / "data")
vault_dir = Path(data_dir / "bank_record.json")


class Currency(Enum):
    PUMPKIN_PESO = ("pk", "南瓜比索")
    AKAONI = ("ak", "AKAONI")
    ANTONINIANUS = ("an", "ANTONINIANUS")
    ADVENTURER_S = ("ad", "ADVENTURER_S")


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

    def get_bank_msg(self, member: Member, c_list: List[Currency]) -> MessageChain:
        user_bank = self.get_bank(member, c_list, chs=True)
        return MessageChain.create(
            [
                At(member),
                Plain(text=" 您的余额为"),
            ] + [
                Plain(text=f" {value} {key}") for key, value in user_bank.items()
            ]
        )

    def get_bank(self, member: Member, c_list: Union[List[Currency]], *, chs: bool = False) -> Dict[str, int]:
        if str(member.id) in self.vault.keys():
            user_bank = {c.value[0 if not chs else 1]: self.vault[str(member.id)].get(c.value[0]) for c in c_list}
        else:
            for c in c_list:
                self.set_bank(member.id, c, 0)
            user_bank = self.get_bank(member, c_list, chs=chs)
        return user_bank

    def store_bank(self) -> NoReturn:
        with open(vault_dir, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.vault, indent=4))

    def load_bank(self) -> NoReturn:
        with open(vault_dir, "r", encoding="utf-8") as f:
            self.vault = json.loads(f.read())

    def update_bank(self, supplicant: int, c: Currency, amount: int) -> int:
        if str(supplicant) in self.vault.keys():
            self.vault[str(supplicant)][c.value[0]] += amount
        else:
            self.vault[str(supplicant)] = {[c.value[0]]: amount}
        self.store_bank()
        return self.vault[str(supplicant)][c.value[0]]

    def set_bank(self, supplicant: int, c: Currency, amount: int) -> int:
        if str(supplicant) in self.vault.keys():
            self.vault[str(supplicant)][c.value[0]] = amount
        else:
            self.vault[str(supplicant)] = {c.value[0]: amount}
        self.store_bank()
        return self.vault[str(supplicant)][c.value[0]]


vault = Vault()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    FullMatch("/bank")
                ]
            )
        ],
        decorators=[BlacklistControl.enable()]
    )
)
async def chitung_bank_handler(
        app: Ariadne,
        event: MessageEvent
):
    await app.sendGroupMessage(event.sender.group, vault.get_bank_msg(event.sender, [Currency.PUMPKIN_PESO]))


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
        decorators=[BlacklistControl.enable()]
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
    vault.set_bank(target, Currency.PUMPKIN_PESO, amount)
    await app.sendGroupMessage(event.sender.group, MessageChain("已设置成功。"))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    FullMatch("/laundry"),
                    RegexMatch(r"\d+") @ "amount"
                ]
            )
        ],
        decorators=[BlacklistControl.enable()]
    )
)
async def chitung_bank_laundry_handler(
        event: MessageEvent,
        amount: RegexResult
):
    if event.sender.id not in config.adminID:
        return
    amount = int(amount.result.asDisplay())
    vault.update_bank(event.sender.id, Currency.PUMPKIN_PESO, amount)
