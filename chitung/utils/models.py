from enum import Enum
from typing import List, Literal, Union

from graia.ariadne import get_running, Ariadne
from graia.ariadne.model import Group, Member
from pydantic import BaseModel


class FunctionControl(BaseModel):
    fish: bool = True
    casino: bool = True
    responder: bool = True
    lottery: bool = True
    game: bool = True


class RequestControl(BaseModel):
    answerFriend: bool = True
    answerGroup: bool = True
    addFriend: bool = True
    addGroup: bool = True
    autoAnswer: bool = True


class CustomizedConfig(BaseModel):
    joinGroupText: str = "很高兴为您服务。在使用本 bot 之前，请仔细阅读下方的免责协议。"
    rejectGroupText: str = "抱歉，机器人暂时不接受加群请求。"
    onlineText: str = "机器人已经上线。"
    welcomeText: str = "欢迎。"
    permissionChangedText: str = "谢谢，各位将获得更多的乐趣。"
    groupNameChangedText: str = "好名字。"
    nudgeText: str = "啥事？"


class Config(BaseModel):
    botName: str = ""
    devGroupID: List[int] = []
    adminID: List[int] = []
    minimumMembers: int = 7
    friendFC: FunctionControl = FunctionControl()
    groupFC: FunctionControl = FunctionControl()
    rc: RequestControl = RequestControl()
    cc: CustomizedConfig = CustomizedConfig()


class GroupSwitch(Enum):
    globalControl = "globalControl"
    fish = "fish"
    casino = "casino"
    responder = "responder"
    lottery = "lottery"
    game = "game"


class GroupConfig(BaseModel):
    groupID: int
    globalControl: bool = True
    fish: bool = True
    casino: bool = True
    responder: bool = True
    lottery: bool = True
    game: bool = True
    blockedUser: List[int] = []


class GroupConfigList(BaseModel):
    groupConfigList: List[GroupConfig] = []

    async def check(self):
        if group_list := await get_running(Ariadne).getGroupList():
            for group in group_list:
                assert isinstance(group, Group)
                if _ := self.get(group.id, create_if_none=False):
                    continue
                self.groupConfigList.append(GroupConfig(groupID=group.id))

    def get(
            self,
            group_id: int,
            *,
            create_if_none: bool = True
    ):
        if group_config := list(filter(
            lambda cfg:
            cfg.groupID == group_id,
            self.groupConfigList
        )):
            return group_config[0]
        elif create_if_none:
            self.groupConfigList.append(GroupConfig(groupID=group_id))
            return self.get(group_id, create_if_none=False)

    def block_member(
            self,
            group: Union[Group, int],
            target: Union[Member, int]
    ):
        group = group.id if isinstance(group, Group) else group
        target = target.id if isinstance(target, Member) else target
        if cfg := self.get(group):
            cfg.blockedUser.append(target)

    def unblock_member(
            self,
            group: Union[Group, int],
            target: Union[Member, int]
    ):
        group = group.id if isinstance(group, Group) else group
        target = target.id if isinstance(target, Member) else target
        if cfg := self.get(group):
            if target in cfg.blockedUser:
                cfg.blockedUser.remove(target)
                return True
            return False

    def alt_setting(
            self,
            group: Union[Group, int],
            setting: GroupSwitch,
            new_value: bool
    ):
        group = group.id if isinstance(group, Group) else group
        if cfg := self.get(group):
            setattr(cfg, setting.value, new_value)


class UniversalRespond(BaseModel):
    messageKind: Literal["Friend", "Group", "Any"]
    listResponseKind: Literal["Friend", "Group"]
    listKind: Literal["Black", "White"]
    userList: List[int]
    triggerKind: Literal["Equal", "Contain"]
    pattern: List[str]
    answer: List[str]


class UniversalRespondList(BaseModel):
    universalRespondList: List[UniversalRespond]


class BlacklistModel(BaseModel):
    friendBlacklist: List[int] = []
    groupBlacklist: List[int] = []


class UniversalImageResponder(BaseModel):
    keyword: List[str]
    directoryName: str
    text: str
    triggerType: Literal['Equal', 'Contain']
    responseType: Literal["Friend", "Group", "Any"]


class UniversalImageResponderList(BaseModel):
    dataList: List[UniversalImageResponder]


class UserPerm(Enum):
    MEMBER = "MEMBER"
    ADMINISTRATOR = "ADMINISTRATOR"
    OWNER = "OWNER"
    BOT_OWNER = "BOT_OWNER"

    def __lt__(self, other: "UserPerm"):
        lv_map = {UserPerm.MEMBER: 1, UserPerm.ADMINISTRATOR: 2, UserPerm.OWNER: 3, UserPerm.BOT_OWNER: 4}
        return lv_map[self] < lv_map[other]
