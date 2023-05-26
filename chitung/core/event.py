from dataclasses import dataclass

from graia.amnesia.message import MessageChain
from graia.broadcast import BaseDispatcher, Dispatchable, DispatcherInterface
from ichika.client import Client
from ichika.core import RawMessageReceipt


@dataclass
class ActiveMessage(Dispatchable):
    client: Client
    receipt: RawMessageReceipt
    content: MessageChain

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: "DispatcherInterface[ActiveMessage]"):  # noqa
            if interface.annotation is RawMessageReceipt:
                return interface.event.receipt
            if interface.annotation is Client:
                return interface.event.client
            if interface.annotation is MessageChain:
                return interface.event.content
