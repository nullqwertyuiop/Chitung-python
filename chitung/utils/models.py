from typing import List, Literal

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


class CommonControl(BaseModel):
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
    cc: CommonControl = CommonControl()


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
    groupConfigList: List[GroupConfig]


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
    remoteBlacklist: List[int] = []
