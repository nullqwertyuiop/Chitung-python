from graia.ariadne import Ariadne
from graia.ariadne.event.lifecycle import ApplicationLaunched
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage
from graia.ariadne.exception import UnknownTarget, AccountMuted
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.twilight import Twilight, UnionMatch, MatchResult, FullMatch, RegexMatch, RegexResult
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from .config import config, group_config, save_group_config, save_config, reset_config
from .models import UserPerm
from ..utils.depends import BlacklistControl, Permission

channel = Channel.current()

channel.name("ChitungAdminTools")
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
                    FullMatch("/adminhelp")
                ]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            Permission.require(UserPerm.BOT_OWNER)
        ]
    )
)
async def chitung_admin_help_handler(
        app: Ariadne,
        event: MessageEvent,
):
    if event.sender.id not in config.adminID:
        return
    await app.sendMessage(
        event.sender.group
        if isinstance(event, GroupMessage)
        else event.sender,
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
        listening_events=[
            GroupMessage,
            FriendMessage
        ],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("/coverage", "/num -f", "/num -g") @ "func"
                ]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            Permission.require(UserPerm.BOT_OWNER)
        ]
    )
)
async def chitung_admin_tools_handler(
        app: Ariadne,
        event: MessageEvent,
        func: MatchResult
):
    func = func.result.asDisplay()
    if func == "/num -f":
        return await app.sendMessage(
            event.sender.group
            if isinstance(event, GroupMessage)
            else event.sender,
            MessageChain(f"七筒目前的好友数量是：{len(await app.getFriendList())}")
        )
    elif func == "/num -g":
        return await app.sendMessage(
            event.sender.group
            if isinstance(event, GroupMessage)
            else event.sender,
            MessageChain(f"七筒目前的群数量是：{len(await app.getGroupList())}")
        )
    else:
        group_list = await app.getGroupList()
        member_list = []
        for group in group_list:
            member_list.extend(await app.getMemberList(group))
        return await app.sendMessage(
            event.sender.group
            if isinstance(event, GroupMessage)
            else event.sender,
            MessageChain(f"七筒目前的覆盖人数是：{len(member_list)}")
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
                    FullMatch("/config"),
                    UnionMatch("-h", "1", "2", "3", "4", "5") @ "option",
                    RegexMatch(r"[Tt]rue|[Ff]alse") @ "value"
                ]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            Permission.require(UserPerm.BOT_OWNER)
        ]
    )
)
async def chitung_config_tools_handler(
        app: Ariadne,
        event: MessageEvent,
        option: MatchResult,
        value: RegexResult
):
    if all([not option.matched,
            not value.matched]):
        await app.sendMessage(
            event.sender.group
            if isinstance(event, GroupMessage)
            else event.sender,
            MessageChain(
                f"addFriend: {config.rc.addFriend}"
                f"addGroup: {config.rc.addGroup}"
                f"answerFriend: {config.rc.answerFriend}"
                f"answerGroup: {config.rc.answerGroup}"
                f"autoAnswer: {config.rc.autoAnswer}"
            )
        )
        return
    option = option.result.asDisplay()
    value = True if value.result.asDisplay().upper()[0] == "T" else False
    if option == "-h":
        await app.sendMessage(
            event.sender.group
            if isinstance(event, GroupMessage)
            else event.sender,
            MessageChain(
                "使用/config+空格+数字序号+空格+true/false来开关配置。\n\n"
                "1:addFriend\n"
                "2:addGroup\n"
                "3:answerFriend\n"
                "4:answerGroup\n"
                "5:autoAnswer"
            )
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
        event.sender.group
        if isinstance(event, GroupMessage)
        else event.sender,
        msg
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
                    FullMatch("/reset"),
                    RegexMatch(r"\s*config")
                ]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            Permission.require(UserPerm.BOT_OWNER)
        ]
    )
)
async def chitung_reset_config_handler(
        app: Ariadne,
        event: MessageEvent
):
    reset_config()
    save_config()
    await app.sendMessage(
        event.sender.group
        if isinstance(event, GroupMessage)
        else event.sender,
        MessageChain("已经重置 Config 配置文件。")
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
