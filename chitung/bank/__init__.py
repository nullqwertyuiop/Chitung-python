import json
import os
import os.path
from enum import Enum
from pathlib import Path
from typing import Union, List

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain
from graia.ariadne.message.parser.twilight import Twilight, FullMatch
from graia.ariadne.model import Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

channel = Channel.current()

channel.name("ChitungBank")
channel.author("角川烈、白门守望者")
channel.description("/bank")

data_dir = Path(Path(__file__).parent / "data")
vault_dir = Path(data_dir / "bank_record.json")


class Currency(Enum):
    PUMPKIN_PESO = ("pk", "南瓜比索")
    AKAONI = ("ak", "AKAONI")
    ANTONINIANUS = ("an", "ANTONINIANUS")
    ADVENTURER_S = ("ad", "ADVENTURER_S")


class Vault:
    def __init__(self):
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)
        if not os.path.exists(vault_dir):
            self.vault = {}
            self.store_bank()
        else:
            self.load_bank()

    def get_bank(self, member: Member, c_list: Union[List[Currency]]) -> MessageChain:
        user_bank = self.get_bank_dict(member, c_list, chs=True)
        return MessageChain.create([
            At(member),
            Plain(text=" 您的余额为"),
        ] + [
            Plain(text=f" {value} {key}") for key, value in user_bank.items()
        ])

    def get_bank_dict(self, member: Member, c_list: Union[List[Currency]], *, chs: bool = False) -> dict:
        if member.id in self.vault.keys():
            user_bank = {c.value[0 if not chs else 1]: self.vault[member.id].get(c.value[0]) for c in c_list}
        else:
            for c in c_list:
                self.set_bank(member.id, c, 0)
            user_bank = self.get_bank_dict(member, c_list, chs=chs)
        return user_bank

    def store_bank(self):
        with open(vault_dir, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.vault, indent=4))

    def load_bank(self):
        with open(vault_dir, "r", encoding="utf-8") as f:
            self.vault = json.loads(f.read())

    def update_bank(self, supplicant: int, c: Currency, amount: int):
        if supplicant in self.vault.keys():
            self.vault[supplicant][c.value[0]] += amount
        else:
            self.vault[supplicant] = {[c.value[0]]: amount}
        self.store_bank()

    def set_bank(self, supplicant: int, c: Currency, amount: int):
        if supplicant in self.vault.keys():
            self.vault[supplicant][c.value[0]] = amount
        else:
            self.vault[supplicant] = {c.value[0]: amount}
        self.store_bank()


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
        ]
    )
)
async def chitung_bank_handler(
        app: Ariadne,
        event: MessageEvent
):
    await app.sendGroupMessage(event.sender.group, vault.get_bank(event.sender, [Currency.PUMPKIN_PESO]))
