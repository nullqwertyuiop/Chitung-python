from pathlib import Path

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.message.parser.twilight import Twilight, UnionMatch, MatchResult, FullMatch
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from ..utils.config import config
from ..utils.depends import BlacklistControl, FunctionControl

channel = Channel.current()

channel.name("ChitungHelp")
channel.author("角川烈&白门守望者 (Chitung-public), nullqwertyuiop (Chitung-python)")
channel.description("七筒")


@channel.use(
    ListenerSchema(
        listening_events=[
            GroupMessage,
            FriendMessage
        ],
        inline_dispatchers=[
            Twilight(
                [
                    FullMatch("/funct")
                ]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            FunctionControl.enable(FunctionControl.Responder)
        ]
    )
)
async def chitung_help_image_handler(
        app: Ariadne,
        event: MessageEvent
):
    await app.sendMessage(
        event.sender.group
        if isinstance(event, GroupMessage)
        else event.sender,
        MessageChain.create([
            Image(path=Path(Path(__file__).parent / "assets" / "help" / "funct.png"))
        ])
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
                    UnionMatch("/help", "intro", "/usage", "/conta") @ "which"
                ]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            FunctionControl.enable(FunctionControl.Responder)
        ]
    )
)
async def chitung_help_desk_handler(
        app: Ariadne,
        event: MessageEvent,
        which: MatchResult
):
    which = which.result.asDisplay()
    if which == "/help":
        msg = MessageChain("输入下方带有斜杠的关键词可以获得相关信息。\n\n"
                           f"/intro {config.botName}简介\n"
                           f"/usage 如何在自己的群中使用{config.botName}\n"
                           f"/discl 免责协议\n"
                           f"/conta 联系营运者和开发者")
    elif which == "/intro":
        msg = MessageChain("本机器人使用基于七筒开放版开发的 Chitung-python——一个致力于服务简体中文 Furry 社群的 QQ 机器人项目，"
                           "皆在试图为群聊增加一些乐趣。请发送/funct 来了解如何使用本机器人。注意，不要和我，也不要和生活太较真。")
    elif which == "/usage":
        msg = MessageChain(f"点击头像添加{config.botName}为好友，并将其邀请到QQ群聊中，即可在该群聊中使用服务。"
                           f"如果需要查看功能列表，请输入/funct。")
    elif which == "/discl":
        msg = MessageChain("本项目由基于七筒开放版开发的 Chitung-python 驱动，但并非由官方直接运营，如有任何问题请联系该机器人的运营者。"
                           "如需使用该项目请查询 Github - Chitung Python，或者联系七筒项目的开发者（见/conta）。")
    else:
        msg = MessageChain(f"如果需要联系{config.botName}的运营者，请直接添加{config.botName}好友，并在发送消息的开头注明”意见反馈“。"
                           f"只有含有“意见反馈”字样的单条消息才会被接收。"
                           f"如需要联系七筒的开发者和体验七筒功能，请添加公众聊天群：932617537。"
                           f"如需要获得七筒的最新消息，请添加通知群：948979109。"
                           f"如需要获得 Chitung-python 的最新消息，请添加群：719381570。")
    await app.sendMessage(
        event.sender.group
        if isinstance(event, GroupMessage)
        else event.sender,
        msg
    )
