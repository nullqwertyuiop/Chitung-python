from typing import List, Literal

from pydantic import BaseModel


class FunctionControl(BaseModel):
    fish: bool
    casino: bool
    responder: bool
    lottery: bool
    game: bool


class RequestControl(BaseModel):
    answerFriend: bool
    answerGroup: bool
    addFriend: bool
    addGroup: bool
    autoAnswer: bool


class CommonControl(BaseModel):
    joinGroupText: str
    rejectGroupText: str
    onlineText: str
    welcomeText: str
    permissionChangedText: str
    groupNameChangedText: str
    nudgeText: str


class Config(BaseModel):
    botName: str
    botID: int
    devGroupID: List[int]
    adminID: List[int]
    minimumMembers: int
    friendFC: FunctionControl
    groupFC: FunctionControl
    rc: RequestControl
    cc: CommonControl


class GroupConfig(BaseModel):
    groupID: int
    globalControl: bool
    fish: bool
    casino: bool
    responder: bool
    lottery: bool
    game: bool
    blockedUser: List[int]


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
