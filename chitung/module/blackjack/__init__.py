import asyncio

from avilla.core import Context, Message, Notice, Picture, Selector
from avilla.standard.core.message import MessageReceived
from avilla.twilight.twilight import (
    FullMatch,
    MatchResult,
    RegexMatch,
    Twilight,
    UnionMatch,
)
from graia.amnesia.message import MessageChain, Text
from graia.saya.builtins.broadcast.shortcut import dispatch, listen
from launart import Launart

from chitung.library.const import ASSETS_ROOT
from chitung.library.service import BankService
from chitung.library.service.bank import Currency

from .blackjack import (
    BOOKMAKER_SELECTOR,
    BlackJackData,
    BlackJackPhase,
    BlackJackPlayer,
)


@listen(MessageReceived)
@dispatch(
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
)
async def chitung_blackjack_ops_handler(ctx: Context, msg: Message):
    function = str(msg.content)
    try:
        if function in {"/deal", "要牌"}:
            await deal(ctx)
        elif function in {"/fold", "停牌"}:
            await fold(ctx)
        elif function in {"/split", "分牌"}:
            await split(ctx)
        elif function in {"/double", "双倍下注"}:
            await double_bet(ctx)
        elif function in {"/pair", "下注对子"}:
            await pair(ctx)
        elif function in {"/assurance", "买保险"}:
            await assurance(ctx)
        elif function in {"/surrender", "投降"}:
            await surrender(ctx)

        bjd, _ = get_valid_game_and_player(ctx)
        if bjd.check_all_fold():
            await checkout_game(ctx)
    except ValueError:
        return


@listen(MessageReceived)
@dispatch(
    Twilight(
        FullMatch("/bet"),
        RegexMatch(r"\s*[0-9]*") @ "amount",
    )
)
async def chitung_blackjack_bet_handler(
    ctx: Context,
    amount: MatchResult,
):
    bets = int(str(amount.result).strip())
    await bet(ctx, bets)


@listen(MessageReceived)
@dispatch(Twilight(UnionMatch("/blackjack", "二十一点")))
async def chitung_blackjack_handler(ctx: Context):
    if ctx.scene in blackjack_sessions:
        return await send_message(ctx, MessageChain("游戏正在进行中。"))
    reply_msg = "里格斯公司邀请您参与本局 Blackjack，请在60秒之内输入 /bet+数字 参与游戏。"
    reply_msg += Picture(ASSETS_ROOT / "blackjack" / "instructions.png")
    await send_message(ctx, MessageChain(reply_msg), False)
    bjd = BlackJackData(ctx.scene)
    blackjack_sessions[ctx.scene] = bjd
    await asyncio.sleep(60)
    if bjd.phase != BlackJackPhase.Callin:
        return
    blackjack_sessions.pop(ctx.scene)
    await send_message(ctx, MessageChain("本局 Blackjack 已经取消。"))


async def bet(ctx: Context, bets: int):
    bjd = get_game_data(ctx.scene)
    if bjd is None:
        return
    if bets <= 0:
        raise ValueError

    if await purchase(ctx.client, bets):
        if bjd.phase == BlackJackPhase.Callin:
            bjd.phase = BlackJackPhase.Bet
            if ctx.client.pattern == bjd.scene.pattern:
                asyncio.create_task(end_bet_phase(ctx, 0))
            else:
                await send_message(
                    ctx,
                    MessageChain("Bet 阶段已经开始，预计在 60 秒之内结束。可以通过 /bet+金额 反复追加 bet。"),
                    False,
                )
                asyncio.create_task(end_bet_phase(ctx))
        if bjd.black_jack_players.get(ctx.client) is None:
            # 新玩家
            prompt = f"已收到下注 {bets} 南瓜比索。"
        else:
            prompt = f"共收到下注 {bets + bjd.black_jack_players.get(ctx.client).bet} 南瓜比索。"
        bjd.bet(ctx.client, bets)
        await send_message(ctx, MessageChain(prompt))
    else:
        await send_message(ctx, MessageChain("操作失败，请检查您的南瓜比索数量。"))


async def end_bet_phase(ctx: Context, time_out: int = 60):
    await asyncio.sleep(time_out)
    bjd = get_game_data(ctx.scene)
    if bjd is None:
        return
    bjd.end_bet()
    await send_message(ctx, MessageChain("Bet 阶段已经结束。"), notice=False)
    reply_msg = MessageChain("抽牌情况如下：\n")
    reply_msg += f"庄家的牌是：\n{bjd.black_jack_players[BOOKMAKER_SELECTOR].cards[0]} 暗牌"
    for player in bjd.black_jack_players.values():
        if player.client.pattern == BOOKMAKER_SELECTOR.pattern:
            continue
        if ctx.scene != ctx.client:  # 判断是不是群
            reply_msg += MessageChain(["\n\n", Notice(player.client), " 的牌是：\n"])
        else:
            reply_msg += MessageChain("\n\n你的牌是：\n")
        reply_msg += f" {player.cards[0]} {player.cards[1]}"
    await send_message(ctx, reply_msg, notice=False)
    await send_message(
        ctx,
        MessageChain("现在可以进行操作，请在 60 秒之内完成。功能列表请参考说明书。"),
        notice=False,
    )
    await end_operate_phase(ctx)


async def end_operate_phase(ctx: Context):
    await asyncio.sleep(60)
    bjd = get_game_data(ctx.scene)
    if bjd is None:
        # 提前结束
        return
    bjd.fold_all()
    await checkout_game(ctx)


async def checkout_game(ctx: Context):
    bjd = get_game_data(ctx.scene)
    # 庄家操作
    bookmaker_pile_msg = bjd.bookmaker_operate()
    await send_message(ctx, MessageChain(bookmaker_pile_msg), False)
    reply_msg = MessageChain("本局游戏已经结束，里格斯公司感谢您的参与。如下为本局玩家获得的南瓜比索：\n")
    result = bjd.check()
    for player in bjd.black_jack_players.values():
        if player.is_bookmaker:
            continue
        if ctx.client.pattern == bjd.scene.pattern:
            reply_msg += f"\n您获得了 {result[player.client]} 南瓜比索。"
        else:
            reply_msg += MessageChain(
                [
                    "\n",
                    Notice(player.client),
                    f" 获得了 {result[player.client]} 南瓜比索。",
                ]
            )
        await exchange(ctx.client, result[player.client])
    blackjack_sessions.pop(ctx.scene)
    await send_message(ctx, reply_msg, notice=False)


async def deal(ctx: Context):
    bjd, player = get_valid_game_and_player(ctx)
    if player.can_operate:
        deal_result = bjd.deal(ctx.client)
        await send_message(ctx, MessageChain(f"您抽到的牌是：{deal_result[0]}"))
        if not deal_result[1]:
            await send_message(ctx, MessageChain("您爆牌了。"))
            bjd.busted(player.client)


async def fold(ctx: Context):
    bjd, player = get_valid_game_and_player(ctx)
    if player.can_operate:
        bjd.fold(player.client)
        await send_message(ctx, MessageChain("您已经停牌。"))
    if bjd.check_all_fold():
        await checkout_game(ctx)


async def split(ctx: Context):
    bjd, player = get_valid_game_and_player(ctx)
    if not player.can_operate:
        return
    if not player.can_split():
        return
    if not purchase(ctx.client, player.bet):
        await send_message(ctx, MessageChain("操作失败，请检查您的南瓜比索数量。"))
        return
    raw_cards, piles = bjd.split(player.client)
    reply_msg = MessageChain(
        f"您的原始牌堆为：\n{raw_cards[0]}{raw_cards[1]}\n您两个牌堆抽到的牌分别是：\n牌堆I："
    )
    for card in piles[0]:
        reply_msg += f" {card}"
    reply_msg += "\n牌堆II："
    for card in piles[1]:
        reply_msg += f" {card}"
    await send_message(ctx, reply_msg, ctx.client != ctx.scene)


async def double_bet(ctx: Context):
    bjd, player = get_valid_game_and_player(ctx)
    if not player.can_operate:
        return
    if not player.can_double_bet():
        await send_message(ctx, MessageChain("您的牌无法双倍下注。"))
        return
    if not purchase(ctx.client, player.bet):
        await send_message(ctx, MessageChain("操作失败，请检查您的南瓜比索数量。"))
        return
    bjd.double_bet(player.client)


async def assurance(ctx: Context):
    bjd, player = get_valid_game_and_player(ctx)
    if not player.can_operate:
        return
    if bjd.assurance(player.client):
        await send_message(ctx, MessageChain("您已经购买保险。"))
    else:
        await send_message(ctx, MessageChain("目前的牌局无法购买保险。"))


async def pair(ctx: Context):
    bjd, player = get_valid_game_and_player(ctx)
    if not player.can_operate:
        return
    if not purchase(ctx.client, player.bet):
        await send_message(ctx, MessageChain("操作失败，请检查您的南瓜比索数量。"))
        return
    if bjd.bet_pair(player.client):
        await send_message(ctx, MessageChain("您已经下注对子。"))
    else:
        await send_message(ctx, MessageChain("无法重复下注对子。"))


async def surrender(ctx: Context):
    bjd, player = get_valid_game_and_player(ctx)
    if not player.can_operate:
        return
    bjd.surrender(player.client)
    await send_message(ctx, MessageChain("您投降了，将会返还您一半的赌注。"))


def get_valid_game_and_player(ctx: Context) -> tuple[BlackJackData, BlackJackPlayer]:
    bjd = get_game_data(ctx.scene)
    if bjd is None:
        raise ValueError
    player = bjd.black_jack_players[ctx.client]
    if player is None:
        raise ValueError
    return bjd, player


async def purchase(target: Selector, cost: int) -> bool:
    vault = Launart.current().get_component(BankService).vault
    if await vault.has_enough(target, Currency.PUMPKIN_PESO, cost):
        await vault.withdraw(target, Currency.PUMPKIN_PESO, cost)
        return True
    return False


async def exchange(target: Selector, num: int):
    vault = Launart.current().get_component(BankService).vault
    await vault.deposit(target, Currency.PUMPKIN_PESO, num)


async def send_message(ctx: Context, msg: MessageChain, notice: bool = True):
    if notice:
        msg.content.insert(0, Notice(ctx.client))
        msg.content.insert(1, Text(" "))
    await ctx.scene.send_message(msg)


def get_game_data(scene: Selector) -> BlackJackData | None:
    return blackjack_sessions[scene] if scene in blackjack_sessions else None


blackjack_sessions: dict[Selector, BlackJackData] = {}
