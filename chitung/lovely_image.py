from graia.ariadne import get_running
from graia.ariadne.adapter import Adapter
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.message.parser.twilight import (
    Twilight,
    UnionMatch,
    MatchResult,
    SpacePolicy,
)
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from .utils.depends import BlacklistControl, FunctionControl


channel = Channel.current()

channel.name("ChitungLovelyImage")
channel.author("角川烈&白门守望者 (Chitung-public), nullqwertyuiop (Chitung-python)")
channel.description("OK Animal")

urls = {
    "husky": "https://dog.ceo/api/breed/husky/images/random",
    "bernese": "https://dog.ceo/api/breed/mountain/bernese/images/random",
    "malamute": "https://dog.ceo/api/breed/malamute/images/random",
    "gsd": "https://dog.ceo/api/breed/germanshepherd/images/random",
    "samoyed": "https://dog.ceo/api/breed/samoyed/images/random",
    "doberman": "https://dog.ceo/api/breed/doberman/images/random",
    "shiba": "https://shibe.online/api/shibes",
    "cat": "https://shibe.online/api/cats",
    "dog": "https://random.dog/woof.json",
}

cord = {
    "dog": ["狗狗", "狗子", "狗"],
    "cat": ["猫猫", "猫", "猫咪", "喵喵"],
    "shiba": ["柴犬", "柴柴"],
    "husky": ["哈士奇", "二哈"],
    "bernese": ["伯恩山", "伯恩山犬"],
    "malamute": ["阿拉斯加"],
    "gsd": ["德牧", "黑背"],
    "doberman": ["杜宾", "dobermann"],
    "samoyed": ["萨摩耶"],
}


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("ok ", "Ok ", "OK ", "/").space(SpacePolicy.NOSPACE),
                    UnionMatch(
                        "Shiba",
                        "shiba",
                        "狗",
                        "柴犬",
                        "伯恩山",
                        "Bernese",
                        "bernese",
                        "狗子",
                        "柴柴",
                        "Husky",
                        "husky",
                        "Doberman",
                        "doberman",
                        "Gsd",
                        "gsd",
                        "GSD",
                        "Dobermann",
                        "dobermann",
                        "喵喵",
                        "猫猫",
                        "二哈",
                        "黑背",
                        "狗狗",
                        "德牧",
                        "萨摩耶",
                        "哈士奇",
                        "Malamute",
                        "malamute",
                        "杜宾",
                        "猫",
                        "伯恩山犬",
                        "阿拉斯加",
                        "Dog",
                        "dog",
                        "Samoyed",
                        "samoyed",
                        "Cat",
                        "cat",
                        "猫咪",
                    )
                    @ "animal",
                ]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            FunctionControl.enable(FunctionControl.Responder),
        ],
    )
)
async def chitung_animal_handler(
    app: Ariadne, event: MessageEvent, animal: MatchResult
):
    key, animal_name = get_animal_name(animal.result.asDisplay())
    await app.sendMessage(
        event.sender.group if isinstance(event, GroupMessage) else event.sender,
        MessageChain(f"正在获取{animal_name}>>>>>>>"),
    )
    await app.sendMessage(
        event.sender.group if isinstance(event, GroupMessage) else event.sender,
        await get_animal_image(key),
    )


async def get_animal_image(animal: str, retry_count: int = 0):
    url = urls.get(animal)
    async with get_running(Adapter).session.get(url=url) as resp:
        if resp.status != 200:
            return MessageChain(f"非常抱歉，获取{cord.get(animal)[0]}图的渠道好像出了一些问题，图片获取失败")
        data = await resp.json()
    if isinstance(data, list):
        img_url = data[0]
    else:
        if "url" in data.keys():
            img_url = data["url"]
        elif "message" in data.keys():
            img_url = data["message"]
        else:
            return MessageChain(f"非常抱歉，获取{cord.get(animal)[0]}图的渠道好像出了一些问题，图片获取失败")
    if all(
        [
            not img_url.endswith("jpg"),
            not img_url.endswith("jpeg"),
            not img_url.endswith("png"),
        ]
    ):
        if retry_count >= 5:
            return MessageChain(f"非常抱歉，获取{cord.get(animal)[0]}图的渠道好像出了一些问题，图片获取失败")
        return await get_animal_image(animal, retry_count + 1)
    return MessageChain.create([Image(url=img_url)])


def get_animal_name(animal: str):
    for key, item in cord.items():
        if animal == key or animal in item:
            return key, item[0]
