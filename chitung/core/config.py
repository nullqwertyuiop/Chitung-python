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
    join_group_text: str = "很高兴为您服务。"
    reject_group_text: str = "抱歉，机器人暂时不接受加群请求。"
    online_text: str = "机器人已经上线。"
    welcome_text: str = "欢迎。"
    permission_changed_text: str = "谢谢，各位将获得更多的乐趣。"
    group_name_changed_text: str = "好名字。"
    nudge_text: str = "啥事？"
