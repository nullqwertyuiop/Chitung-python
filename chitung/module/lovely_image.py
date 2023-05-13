import re

from creart import it
from graia.amnesia.message import MessageChain, Text
from graia.saya import Channel
from graiax.shortcut import decorate, listen
from graiax.shortcut.text_parser import MatchRegex
from ichika.client import Client
from ichika.core import Friend, Group
from ichika.graia.event import FriendMessage, GroupMessage
from ichika.message.elements import Image

from chitung.core.decorator import FunctionType, Switch
from chitung.core.session import SessionContainer
from chitung.core.util import send_message

channel = Channel.current()

URLS = {
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
NAME_MAP = {
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


def get_all_names() -> set[str]:
    names = set()
    for k, v in NAME_MAP.items():
        names.update({k, k.title()})
        names.update(v)
        names.update({i.title() for i in v})
    return names


REGEX_STR = rf"^(?:\/|(?:\/?[Oo][Kk] ?))({'|'.join(get_all_names())})$"


@listen(GroupMessage, FriendMessage)
@decorate(MatchRegex(REGEX_STR), Switch.check(FunctionType.RESPONDER))
async def animal_handler(client: Client, target: Group | Friend, content: MessageChain):
    key, animal_name = get_animal_name(re.search(REGEX_STR, str(content))[1])
    await send_message(
        client, target, MessageChain([Text(f"正在获取{animal_name}>>>>>>>")])
    )
    await send_message(client, target, await get_animal_image(key))


class _GetImageFailed(Exception):
    pass


async def get_animal_image(animal: str, retry_count: int = 0):
    url = URLS.get(animal)
    session = it(SessionContainer).get(channel.module)
    try:
        async with session.get(url=url) as resp:
            if resp.status != 200:
                raise _GetImageFailed
            data = await resp.json()
        if isinstance(data, list):
            img_url = data[0]
        elif "url" in data.keys():
            img_url = data["url"]
        elif "message" in data.keys():
            img_url = data["message"]
        else:
            raise _GetImageFailed
        if all(
            [
                not img_url.endswith("jpg"),
                not img_url.endswith("jpeg"),
                not img_url.endswith("png"),
            ]
        ):
            if retry_count >= 5:
                raise _GetImageFailed
            else:
                return await get_animal_image(animal, retry_count + 1)
        async with session.get(url=img_url) as resp:
            if resp.status != 200:
                raise _GetImageFailed
            return MessageChain([Image.build(await resp.read())])
    except _GetImageFailed:
        return MessageChain(
            [Text(f"非常抱歉，获取{NAME_MAP.get(animal)[0]}图的渠道好像出了一些问题，图片获取失败")]
        )


def get_animal_name(animal: str):
    animal = animal.lower()
    for key, item in NAME_MAP.items():
        if animal == key or animal in item:
            return key, item[0]
