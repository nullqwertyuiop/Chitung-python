from pathlib import Path

from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.twilight import Twilight, UnionMatch, MatchResult, FullMatch
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from .config import config
from ..utils.depends import BlacklistControl

channel = Channel.current()

channel.name("ChitungAdminTools")
channel.author("角川烈&白门守望者 (Chitung-public), nullqwertyuiop (Chitung-python)")
channel.description("七筒")

winner_dir = Path(Path(__file__).parent / "assets")
c4_activation_flags = []


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    FullMatch("/adminhelp")
                ]
            )
        ],
        decorators=[BlacklistControl.enable()]
    )
)
async def chitung_admin_help_handler(
        app: Ariadne,
        event: MessageEvent,
):
    if event.sender.id not in config.adminID:
        return
    await app.sendGroupMessage(
        event.sender.group,
        MessageChain("Bank：\n"
                     "/laundry 空格 金额：为自己增加/减少钱\n"
                     "/set 空格 QQ号 空格 钱：设置用户的钱的数量\n"
                     "/bank 空格 QQ号：查询用户的钱的数量\n\n"
                     # "Broadcast:\n"
                     # "/broadcast -f 或者 -g：进行好友或者群聊广播\n\n"
                     # "Reset：\n"
                     # "/reset 空格 ur：重置通用响应的配置文件\n"
                     # "/reset 空格 ir：重置通用图库响应的配置文件\n"
                     # "/reset 空格 config：重置 Config 配置文件\n\n"
                     # "Blacklist：\n"
                     # "/block 空格 -g 或者 -f 空格 QQ号：屏蔽该号码的群聊或者用户\n"
                     # "/unblock 空格 -g 或者 -f 空格 QQ号：解除屏蔽该号码的群聊或者用户\n\n"
                     # "Config：\n"
                     # "/config -h：查看 config 的帮助\n"
                     # "/config 空格 数字序号 空格 true/false：开关相应配置\n\n"
                     "Data：\n"
                     "/num -f：查看好友数量\n"
                     "/num -g：查看群聊数量\n"
                     "/coverage：查看总覆盖人数")
    )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("/coverage", "/num -f", "/num -g") @ "func"
                ]
            )
        ],
        decorators=[BlacklistControl.enable()]
    )
)
async def chitung_admin_tools_handler(
        app: Ariadne,
        event: MessageEvent,
        func: MatchResult
):
    if event.sender.id not in config.adminID:
        return
    func = func.result.asDisplay()
    if func == "/num -f":
        return await app.sendGroupMessage(
            event.sender.group,
            MessageChain(f"七筒目前的好友数量是：{len(await app.getFriendList())}")
        )
    elif func == "/num -g":
        return await app.sendGroupMessage(
            event.sender.group,
            MessageChain(f"七筒目前的群数量是：{len(await app.getGroupList())}")
        )
    else:
        group_list = await app.getGroupList()
        member_list = []
        for group in group_list:
            member_list.extend(await app.getMemberList(group))
        return await app.sendGroupMessage(
            event.sender.group,
            MessageChain(f"七筒目前的覆盖人数是：{len(member_list)}")
        )
