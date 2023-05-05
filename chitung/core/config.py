from dataclasses import field

from kayaku import config


@config("chitung.core")
class ChitungConfig:
    account: str = "80000000:password"
    """ 机器人账号，使用冒号分隔账号密码，无指定密码则表明使用二维码登录 """

    bot_name: str = "七筒"
    """ 机器人名字 """

    dev_group_id: list[int] = field(default_factory=list)
    """ 管理员群 """

    admin_id: list[int] = field(default_factory=list)
    """ 管理员名单 """

    minimum_members: int = 7
    """ 最小的群聊人数 """


@config("chitung.nest.friend_fc")
class FriendFCConfig:
    fish: bool = True
    casino: bool = True
    responder: bool = True
    lottery: bool = True
    game: bool = True


@config("chitung.nest.group_fc")
class GroupFCConfig:
    fish: bool = True
    casino: bool = True
    responder: bool = True
    lottery: bool = True
    game: bool = True


@config("chitung.nest.rc")
class RCConfig:
    answer_friend: bool = True
    answer_group: bool = True
    add_friend: bool = True
    add_group: bool = True
    auto_answer: bool = True


@config("chitung.nest.cc")
class CCConfig:
    joinGroupText: str = "很高兴为您服务。"
    rejectGroupText: str = "抱歉，机器人暂时不接受加群请求。"
    onlineText: str = "机器人已经上线。"
    welcomeText: str = "欢迎。"
    permissionChangedText: str = "谢谢，各位将获得更多的乐趣。"
    groupNameChangedText: str = "好名字。"
    nudgeText: str = "啥事？"
