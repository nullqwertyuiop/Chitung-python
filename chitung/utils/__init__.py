from graia.ariadne import Ariadne
from graia.ariadne.event.lifecycle import ApplicationLaunched
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage
from graia.ariadne.exception import UnknownTarget, AccountMuted
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.twilight import (
    Twilight,
    UnionMatch,
    MatchResult,
    FullMatch,
    RegexMatch,
    RegexResult,
    SpacePolicy,
)
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from .config import config, group_config, save_group_config, save_config, reset_config
from .models import UserPerm
from ..utils.depends import BlacklistControl, Permission

channel = Channel.current()

channel.name("ChitungAdminTools")
channel.author(
    "角川烈&白门守望者 (Chitung-public), IshikawaKaito&nullqwertyuiop (Chitung-python)"
)
channel.description("七筒")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[Twilight([FullMatch("/adminhelp")])],
        decorators=[BlacklistControl.enable(), Permission.require(UserPerm.BOT_OWNER)],
    )
)
async def chitung_admin_help_handler(
    app: Ariadne,
    event: MessageEvent,
):
    if event.sender.id not in config.adminID:
        return
    await app.sendMessage(
        event.sender.group if isinstance(event, GroupMessage) else event.sender,
        MessageChain(
            "Bank：\n"
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
            "Config：\n"
            "/config -h：查看 config 的帮助\n"
            "/config 空格 数字序号 空格 true/false：开关相应配置\n\n"
            "Data：\n"
            "/num -f：查看好友数量\n"
            "/num -g：查看群聊数量\n"
            "/coverage：查看总覆盖人数"
        ),
    )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[
            Twilight([UnionMatch("/coverage", "/num -f", "/num -g") @ "func"])
        ],
        decorators=[BlacklistControl.enable(), Permission.require(UserPerm.BOT_OWNER)],
    )
)
async def chitung_admin_tools_handler(
    app: Ariadne, event: MessageEvent, func: MatchResult
):
    func = func.result.asDisplay()
    if func == "/num -f":
        return await app.sendMessage(
            event.sender.group if isinstance(event, GroupMessage) else event.sender,
            MessageChain(f"七筒目前的好友数量是：{len(await app.getFriendList())}"),
        )
    elif func == "/num -g":
        return await app.sendMessage(
            event.sender.group if isinstance(event, GroupMessage) else event.sender,
            MessageChain(f"七筒目前的群数量是：{len(await app.getGroupList())}"),
        )
    else:
        group_list = await app.getGroupList()
        member_list = []
        for group in group_list:
            member_list.extend(await app.getMemberList(group))
        return await app.sendMessage(
            event.sender.group if isinstance(event, GroupMessage) else event.sender,
            MessageChain(f"七筒目前的覆盖人数是：{len(member_list)}"),
        )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[
            Twilight(
                [
                    FullMatch("/config"),
                    UnionMatch("-h", "1", "2", "3", "4", "5", optional=True) @ "option",
                    RegexMatch(r"[Tt]rue|[Ff]alse", optional=True) @ "value",
                ]
            )
        ],
        decorators=[BlacklistControl.enable(), Permission.require(UserPerm.BOT_OWNER)],
    )
)
async def chitung_config_tools_handler(
    app: Ariadne, event: MessageEvent, option: MatchResult, value: RegexResult
):
    if all([not option.matched, not value.matched]):
        await app.sendMessage(
            event.sender.group if isinstance(event, GroupMessage) else event.sender,
            MessageChain(
                f"addFriend: {config.rc.addFriend}\n"
                f"addGroup: {config.rc.addGroup}\n"
                f"answerFriend: {config.rc.answerFriend}\n"
                f"answerGroup: {config.rc.answerGroup}\n"
                f"autoAnswer: {config.rc.autoAnswer}\n"
            ),
        )
        return
    option = option.result.asDisplay()
    if value.matched:
        value = True if value.result.asDisplay().upper()[0] == "T" else False
    if option == "-h":
        await app.sendMessage(
            event.sender.group if isinstance(event, GroupMessage) else event.sender,
            MessageChain(
                "使用/config+空格+数字序号+空格+true/false来开关配置。\n\n"
                "1:addFriend\n"
                "2:addGroup\n"
                "3:answerFriend\n"
                "4:answerGroup\n"
                "5:autoAnswer"
            ),
        )
        return
    elif option == "1":
        config.rc.addFriend = value
        msg = MessageChain(f"已设置addFriend为{value}")
    elif option == "2":
        config.rc.addGroup = value
        msg = MessageChain(f"已设置addGroup为{value}")
    elif option == "3":
        config.rc.answerFriend = value
        msg = MessageChain(f"已设置answerFriend为{value}")
    elif option == "4":
        config.rc.answerGroup = value
        msg = MessageChain(f"已设置answerGroup为{value}")
    else:
        config.rc.autoAnswer = value
        msg = MessageChain(f"已设置autoAnswer为{value}")
    save_config()
    await app.sendMessage(
        event.sender.group if isinstance(event, GroupMessage) else event.sender, msg
    )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[Twilight([FullMatch("/reset"), RegexMatch(r"\s*config")])],
        decorators=[BlacklistControl.enable(), Permission.require(UserPerm.BOT_OWNER)],
    )
)
async def chitung_reset_config_handler(app: Ariadne, event: MessageEvent):
    reset_config()
    save_config()
    await app.sendMessage(
        event.sender.group if isinstance(event, GroupMessage) else event.sender,
        MessageChain("已经重置 Config 配置文件。"),
    )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    FullMatch("/").space(SpacePolicy.NOSPACE),
                    UnionMatch("open", "close") @ "option",
                    UnionMatch(
                        "global",
                        "fish",
                        "casino",
                        "responder",
                        "game",
                        "lottery",
                        optional=True,
                    )
                    @ "funct",
                ]
            )
        ],
        decorators=[BlacklistControl.enable(), Permission.require(UserPerm.BOT_OWNER)],
    )
)
async def chitung_group_config_handler(
    app: Ariadne, event: GroupMessage, option: MatchResult, funct: MatchResult
):
    funct_type = {
        "global": "全局消息",
        "fish": "钓鱼",
        "casino": "娱乐游戏",
        "responder": "关键词触发功能",
        "game": "所有游戏",
        "lottery": "C4和Bummer功能",
    }
    if not funct.matched:
        await app.sendGroupMessage(
            event.sender.group,
            MessageChain(
                "群设置指示词使用错误，"
                "使用/close或者/open加上空格加上"
                "global、game、casino、responder、fish"
                "或者lottery来开关相应内容。"
            ),
        )
        return
    funct = funct.result.asDisplay()
    value = option.result.asDisplay() == "open"
    gc = group_config.get(event.sender.group.id)
    setattr(gc, funct.replace("global", "globalControl"), value)
    save_group_config()
    await app.sendGroupMessage(
        event.sender.group,
        MessageChain(f"已设置{funct_type[funct]}的响应状态为{str(value).lower()}"),
    )


@channel.use(ListenerSchema(listening_events=[ApplicationLaunched]))
async def chitung_init_handler(app: Ariadne):
    await group_config.check()
    save_group_config()
    for group in config.devGroupID:
        try:
            await app.sendGroupMessage(group, MessageChain(config.cc.onlineText))
        except (UnknownTarget, AccountMuted):
            continue
