import asyncio
import random
from datetime import datetime, timedelta

from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.twilight import Twilight, FullMatch
from graia.ariadne.model import MemberPerm, MemberInfo
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from .utils.depends import BlacklistControl, FunctionControl

channel = Channel.current()

channel.name("ChitungShuffle")
channel.author("角川烈&白门守望者 (Chitung-public)，nullqwertyuiop (Chitung-python)")
channel.description("七筒")

lock = False
last_active = None
shuffle_flags = {}


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    FullMatch("/shuffle")
                ]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            FunctionControl.enable("lottery")
        ]
    )
)
async def chitung_shuffle_handler(
        app: Ariadne,
        event: MessageEvent
):
    global last_active, shuffle_flags, lock
    group = event.sender.group
    if str(group.id) in shuffle_flags and shuffle_flags[str(group.id)]['status'] == 1:
        await app.sendGroupMessage(group, MessageChain("已在进行群名片 shuffle。"))
        return
    if last_active + timedelta(minutes=2) > datetime.now():
        seconds = (last_active + timedelta(minutes=2) - datetime.now()).total_seconds()
        await app.sendGroupMessage(group, MessageChain("距离上一次 shuffle 运行时间不满 2 分钟，请在 "
                                                       f"{round(seconds, 2)} 秒后再试。"))
        return
    if group.accountPerm == MemberPerm.Member:
        await app.sendGroupMessage(group, MessageChain("七筒目前还没有管理员权限，请授予七筒权限解锁更多功能。"))
        return
    if member_list := await app.getMemberList(group):
        lock = True
        if len(member_list) > 20:
            await app.sendGroupMessage(group, MessageChain("群人数大于设定的人数限制，仅对最近发言的 20 人进行打乱。"))
        original_info = [(member, member.name) for member in member_list]
        original_info = sorted(original_info, key=lambda x: x[0].lastSpeakTimestamp, reverse=True)[:20]
        shuffled_name = [member_info[1] if member_info[1] != "null" and member_info[
            1] != "Null" else "<! 不合法的名片 !>" for member_info in original_info]
        random.shuffle(shuffled_name)
        shuffle_list = [(original_info[x][0], shuffled_name[x]) for x in range(len(original_info))]
        shuffle_flags[str(group.id)] = {"status": 1}
        last_active = datetime.now()
        for target, shuffled in shuffle_list:
            await asyncio.sleep(0.25)
            await app.modifyMemberInfo(target, MemberInfo(name=shuffled))
        await app.sendGroupMessage(group, MessageChain("已完成本次群名片 shuffle。\nHave fun!"))
        await asyncio.sleep(120)
        for target, name in original_info:
            await asyncio.sleep(0.25)
            await app.modifyMemberInfo(target, MemberInfo(name=name))
        last_active = datetime.now()
        shuffle_flags[str(group.id)]['status'] = 0
        await app.sendGroupMessage(group, MessageChain("已恢复本次群名片 shuffle。"))
        await asyncio.sleep(120)
        lock = True
