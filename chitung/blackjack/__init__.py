import asyncio
from pathlib import Path
from typing import List

from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, At
from graia.ariadne.message.parser.twilight import (
    Twilight,
    UnionMatch,
    MatchResult,
    RegexMatch,
    FullMatch,
)
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from .blackjack import BlackJackData, BlackJackPhase
from ..bank import vault, Currency
from ..utils.depends import BlacklistControl, FunctionControl
from ..utils.priority import priority

channel = Channel.current()

channel.name("ChitungBlackJack")
channel.author("角川烈&白门守望者 (Chitung-public), IshikawaKaito (Chitung-python)")
channel.description("您爆牌了。")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch(
                        "/deal",
                        "/fold",
                        "/split",
                        "/double",
                        "/pair",
                        "/assurance",
                        "/surrender",
                        "要牌",
                        "停牌",
                        "分牌",
                        "双倍下注",
                        "下注对子",
                        "买保险",
                        "投降",
                    )
                    @ "function",
                ]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            FunctionControl.enable(FunctionControl.Casino),
        ],
        priority=priority.Function,
    )
)
async def chitung_blackjack_ops_handler(
    app: Ariadne, event: MessageEvent, function: MatchResult
):
    game_id = (
        event.sender.group.id if isinstance(event, GroupMessage) else event.sender.id
    )
    try:
        if function.result.asDisplay() in ["/deal", "要牌"]:
            await deal(app, event, game_id)
        elif function.result.asDisplay() in ["/fold", "停牌"]:
            await fold(app, event, game_id)
        elif function.result.asDisplay() in ["/split", "分牌"]:
            await split(app, event, game_id)
        elif function.result.asDisplay() in ["/double", "双倍下注"]:
            await double_bet(app, event, game_id)
        elif function.result.asDisplay() in ["/pair", "下注对子"]:
            await pair(app, event, game_id)
        elif function.result.asDisplay() in ["/assurance", "买保险"]:
            await assurance(app, event, game_id)
        elif function.result.asDisplay() in ["/surrender", "投降"]:
            await surrender(app, event, game_id)

        bjd, _ = get_valid_game_and_player(event, game_id)
        if bjd.check_all_fold():
            await checkout_game(app, event, game_id)
    except ValueError:
        return


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[
            Twilight(
                [
                    FullMatch("/bet"),
                    RegexMatch(r"\s*[0-9]*") @ "amount",
                ]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            FunctionControl.enable(FunctionControl.Casino),
        ],
    )
)
async def chitung_blackjack_bet_handler(
    app: Ariadne,
    event: MessageEvent,
    amount: MatchResult,
):
    if isinstance(event, GroupMessage):
        game_id = event.sender.group.id
    else:
        game_id = event.sender.id

    bets = int(amount.result.asDisplay().strip())
    await bet(app, event, game_id, bets)


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[
            Twilight(
                [
                    UnionMatch("/blackjack", "二十一点"),
                ]
            )
        ],
        decorators=[
            BlacklistControl.enable(),
            FunctionControl.enable(FunctionControl.Casino),
        ],
    )
)
async def chitung_blackjack_handler(
    app: Ariadne,
    event: MessageEvent,
):
    if isinstance(event, GroupMessage):
        game_id = event.sender.group.id
    else:
        game_id = event.sender.id

    if len([game for game in blackjack_game_data if game.id == game_id]) != 0:
        await send_message(app, event, "游戏正在进行中。")
    else:
        reply_msg = "里格斯公司邀请您参与本局 Blackjack，请在60秒之内输入 /bet+数字 参与游戏。"
        reply_msg += Image(path=assets_dir / "blackjack.png")
        await send_message(app, event, reply_msg, False)
        bjd = BlackJackData(game_id)
        blackjack_game_data.append(bjd)
        await asyncio.sleep(60)
        if bjd.phase == BlackJackPhase.Callin:
            blackjack_game_data.remove(bjd)
            await send_message(app, event, "本局 Blackjack 已经取消。")
        else:
            return


async def bet(app, event, game_id, bets):
    bjd = get_game_data(game_id)
    if bjd is None:
        return
    if bets <= 0:
        raise ValueError

    if purchase(event.sender, bets):
        if bjd.phase == BlackJackPhase.Callin:
            bjd.phase = BlackJackPhase.Bet
            if event.sender.id == bjd.id:
                asyncio.create_task(end_bet_phase(app, event, game_id, 0))
            else:
                await send_message(
                    app, event, "Bet 阶段已经开始，预计在60秒之内结束。可以通过/bet+金额反复追加 bet。", False
                )
                asyncio.create_task(end_bet_phase(app, event, game_id))
        if bjd.get_player(event.sender.id) is None:
            # 新玩家
            prompt = f"已收到下注{bets}南瓜比索。"
        else:
            prompt = f"共收到下注{bets + bjd.get_player(event.sender.id).bet}南瓜比索。"
        bjd.bet(event.sender.id, bets)
        await send_message(app, event, prompt)
    else:
        await send_message(app, event, "操作失败，请检查您的南瓜比索数量。")


async def end_bet_phase(app, event, game_id, time_out=60):
    await asyncio.sleep(time_out)
    bjd = get_game_data(game_id)
    if bjd is None:
        return
    bjd.end_bet()
    await send_message(app, event, "Bet 阶段已经结束。", at=False)
    reply_msg = MessageChain.create("抽牌情况如下：\n")
    reply_msg += f"庄家的牌是：\n{bjd.get_player(0).cards[0]} 暗牌"
    for player in bjd.black_jack_players:
        if player.player_id == 0:
            continue
        if event.sender.id != game_id:  # 判断是不是群
            reply_msg += MessageChain.create("\n\n", At(player.player_id), " 的牌是：\n")
        else:
            reply_msg += MessageChain.create("\n\n你的牌是：\n")
        reply_msg += f" {player.cards[0]} {player.cards[1]}"
    await send_message(app, event, reply_msg, at=False)
    await send_message(app, event, "现在可以进行操作，请在60秒之内完成。功能列表请参考说明书。", at=False)
    await end_operate_phase(app, event, game_id)


async def end_operate_phase(app, event, game_id):
    await asyncio.sleep(60)
    bjd = get_game_data(game_id)
    if bjd is None:
        # 提前结束
        return
    bjd.fold_all()
    await checkout_game(app, event, game_id)


async def checkout_game(app, event, game_id):
    bjd = get_game_data(game_id)
    # 庄家操作
    bookmaker_pile_msg = bjd.bookmaker_operate()
    await send_message(app, event, bookmaker_pile_msg, False)
    reply_msg = MessageChain.create("本局游戏已经结束，里格斯公司感谢您的参与。如下为本局玩家获得的南瓜比索：\n")
    result = bjd.check()
    for p in bjd.black_jack_players:
        if p.is_bookmaker:
            continue
        if event.sender.id == bjd.id:
            reply_msg += f"\n您获得了{result[p.player_id]}南瓜比索。"
        else:
            reply_msg += MessageChain.create(
                "\n", At(p.player_id), f" 获得了{result[p.player_id]}南瓜比索。"
            )
        exchange(p.player_id, result[p.player_id])
    blackjack_game_data.remove(bjd)
    await send_message(app, event, reply_msg, at=False)


async def deal(app, event, game_id):
    bjd, player = get_valid_game_and_player(event, game_id)
    if player.can_operate:
        deal_result = bjd.deal(event.sender.id)
        await send_message(app, event, f"您抽到的牌是：{deal_result[0]}")
        if not deal_result[1]:
            await send_message(app, event, "您爆牌了。")
            bjd.busted(player.player_id)


async def fold(app, event, game_id):
    bjd, player = get_valid_game_and_player(event, game_id)
    if player.can_operate:
        bjd.fold(player.player_id)
        await send_message(app, event, "您已经停牌。")
    if bjd.check_all_fold():
        await checkout_game(app, event, game_id)


async def split(app, event, game_id):
    bjd, player = get_valid_game_and_player(event, game_id)
    if not player.can_operate:
        return
    if not player.can_split():
        return
    if not purchase(event.sender, player.bet):
        await send_message(app, event, "操作失败，请检查您的南瓜比索数量。")
        return
    raw_cards, piles = bjd.split(player.player_id)
    reply_msg = MessageChain.create(
        f"您的原始牌堆为：\n{raw_cards[0]}{raw_cards[1]}\n您两个牌堆抽到的牌分别是：\n牌堆I："
    )
    for card in piles[0]:
        reply_msg += f" {card}"
    reply_msg += "\n牌堆II："
    for card in piles[1]:
        reply_msg += f" {card}"
    await send_message(app, event, reply_msg, game_id != event.sender.id)


async def double_bet(app, event, game_id):
    bjd, player = get_valid_game_and_player(event, game_id)
    if not player.can_operate:
        return
    if not player.can_double_bet():
        await send_message(app, event, "您的牌无法双倍下注。")
        return
    if not purchase(event.sender, player.bet):
        await send_message(app, event, "操作失败，请检查您的南瓜比索数量。")
        return
    bjd.double_bet(player.player_id)


async def assurance(app, event, game_id):
    bjd, player = get_valid_game_and_player(event, game_id)
    if not player.can_operate:
        return
    if bjd.assurance(player.player_id):
        await send_message(app, event, "您已经购买保险。")
    else:
        await send_message(app, event, "目前的牌局无法购买保险。")


async def pair(app, event, game_id):
    bjd, player = get_valid_game_and_player(event, game_id)
    if not player.can_operate:
        return
    if not purchase(event.sender, player.bet):
        await send_message(app, event, "操作失败，请检查您的南瓜比索数量。")
        return
    if bjd.bet_pair(player.player_id):
        await send_message(app, event, "您已经下注对子。")
    else:
        await send_message(app, event, "无法重复下注对子。")


async def surrender(app, event, game_id):
    bjd, player = get_valid_game_and_player(event, game_id)
    if not player.can_operate:
        return
    bjd.surrender(player.player_id)
    await send_message(app, event, "您投降了，将会返还您一半的赌注。")


def get_valid_game_and_player(event, game_id):
    bjd = get_game_data(game_id)
    if bjd is None:
        raise ValueError
    player = bjd.get_player(event.sender.id)
    if player is None:
        raise ValueError
    return bjd, player


def purchase(sender, cost) -> bool:
    if vault.has_enough_money(sender, Currency.CUCUMBER_PESO, cost):
        vault.update_bank(sender.id, -cost, Currency.CUCUMBER_PESO)
        return True
    else:
        return False


def exchange(player_id, num):
    vault.update_bank(player_id, num, Currency.CUCUMBER_PESO)


async def send_message(app, event, msg, at=True):
    if isinstance(event, GroupMessage):
        if at:
            msg = MessageChain.create(At(event.sender), msg)
        await app.sendGroupMessage(event.sender.group, MessageChain.create(msg))
    else:
        await app.sendFriendMessage(event.sender, MessageChain.create(msg))


def get_game_data(game_id):
    res = [game for game in blackjack_game_data if game.id == game_id]
    if len(res) != 1:
        return None
    return res[0]


assets_dir = Path(Path(__file__).parent / "assets")
blackjack_game_data: List[BlackJackData] = []
