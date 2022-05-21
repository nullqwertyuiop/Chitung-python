import asyncio
import math
import random
from datetime import datetime
from io import BytesIO
from pathlib import Path

from PIL import Image as PillowImage
from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.message.element import Plain, At
from graia.ariadne.message.parser.twilight import (
    Twilight,
    UnionMatch,
    SpacePolicy,
    FullMatch,
)
from graia.ariadne.model import MemberPerm
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema

from ..utils.depends import BlacklistControl, FunctionControl


channel = Channel.current()

channel.name("ChitungLottery")
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
                    UnionMatch("ok ", "Ok ", "OK ", "/").space(SpacePolicy.NOSPACE),
                    FullMatch("winner"),
                ]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            FunctionControl.enable(FunctionControl.Lottery),
        ],
    )
)
async def chitung_winner_handler(app: Ariadne, event: MessageEvent):
    if member_list := await app.getMemberList(event.sender.group):
        now = datetime.now()
        guy_of_the_day = member_list[
            int(
                (now.year + now.month * 10000 + now.day * 1000000)
                * 100000000000
                / event.sender.group.id
                % len(member_list)
            )
        ]
        await app.sendGroupMessage(
            event.sender.group, MessageChain(f"Ok Winner! {guy_of_the_day.name}")
        )
        avatar = PillowImage.open(BytesIO(await guy_of_the_day.getAvatar())).resize(
            (512, 512)
        )
        base = PillowImage.open(Path(winner_dir / "winner" / "wanted.jpg"))
        base.paste(avatar, (94, 251))
        output = BytesIO()
        base.save(output, "jpeg")
        await app.sendGroupMessage(
            event.sender.group,
            MessageChain.create(
                [
                    Image(data_bytes=output.getvalue()),
                ]
            ),
        )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("ok ", "Ok ", "OK ", "/").space(SpacePolicy.NOSPACE),
                    FullMatch("bummer"),
                ]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            FunctionControl.enable(FunctionControl.Lottery),
        ],
    )
)
async def chitung_bummer_handler(app: Ariadne, event: GroupMessage):
    group = event.sender.group
    member = event.sender
    if group.accountPerm == MemberPerm.Member:
        await app.sendGroupMessage(group, MessageChain("七筒目前还没有管理员权限，请授予七筒权限解锁更多功能。"))
        return
    if member_list := await app.getMemberList(group):
        if normal_members := [
            m for m in member_list if m.permission == MemberPerm.Member
        ]:
            victim = random.choice(normal_members)
            await app.muteMember(group, victim, 120)
            if member.permission == MemberPerm.Member:
                if member.id != victim.id:
                    await app.muteMember(group, member, 120)
                    await app.sendGroupMessage(
                        group,
                        MessageChain.create(
                            [
                                Plain(f"Ok Bummer! {victim.name}\n"),
                                At(member),
                                Plain(" 以自己为代价随机带走了 "),
                                At(victim),
                            ]
                        ),
                    )
                    return
                await app.sendGroupMessage(
                    group,
                    MessageChain.create(
                        [
                            Plain(
                                text=f"Ok Bummer! {victim.name}\n"
                                f"{member.name} 尝试随机极限一换一。他成功把自己换出去了！"
                            )
                        ]
                    ),
                )
                return
            await app.sendGroupMessage(
                group,
                MessageChain.create(
                    [
                        Plain(f"Ok Bummer! {victim.name}\n管理员"),
                        At(member),
                        Plain(" 随机带走了 "),
                        At(victim),
                    ]
                ),
            )
        else:
            await app.sendGroupMessage(group, MessageChain("全都是管理员的群你让我抽一个普通成员禁言？别闹。"))

        return


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("ok ", "Ok ", "OK ", "/").space(SpacePolicy.NOSPACE),
                    FullMatch("c4"),
                ]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            FunctionControl.enable(FunctionControl.Lottery),
        ],
    )
)
async def chitung_c4_handler(app: Ariadne, event: MessageEvent):
    group = event.sender.group
    member = event.sender
    if group.accountPerm == MemberPerm.Member:
        await app.sendGroupMessage(group, MessageChain("七筒目前还没有管理员权限，请授予七筒权限解锁更多功能。"))
        return
    if group.id in c4_activation_flags:
        await app.sendGroupMessage(
            group, MessageChain.create("今日的C4已经被触发过啦！请明天再来尝试作死！")
        )
        return
    if member_list := await app.getMemberList(group):
        if random.random() < 1 / math.sqrt(len(member_list)):
            await app.muteAll(group)
            c4_activation_flags.append(group.id)
            await app.sendGroupMessage(group, MessageChain.create("中咧！"))
            await app.sendGroupMessage(
                group,
                MessageChain.create([At(member), Plain(text=" 成功触发了C4！大家一起恭喜TA！")]),
            )
            await asyncio.sleep(300)
            await app.unmuteAll(group)
        else:
            await app.sendGroupMessage(group, MessageChain.create("没有中！"))


@channel.use(SchedulerSchema(timer=timers.crontabify("0 6 * * *")))
async def chitung_c4_flush():
    global c4_activation_flags
    c4_activation_flags = []
