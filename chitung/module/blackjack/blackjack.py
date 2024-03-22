import itertools
import random
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Final

from avilla.core import Selector

DECK_NUM: int = 4
BOOKMAKER_SELECTOR: Final[Selector] = Selector()


class BlackJackPhase(Enum):
    Callin = auto()
    Bet = auto()
    Operation = auto()


class PokerSuit(str, Enum):
    Diamond = "♦"
    Club = "♣"
    Heart = "♥"
    Spade = "♠"

    @staticmethod
    def get(index: int):
        return [PokerSuit.Diamond, PokerSuit.Club, PokerSuit.Heart, PokerSuit.Spade][
            index
        ]


class Poker:
    _poker_name: Final[str] = [
        "A",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "J",
        "Q",
        "K",
    ]

    def __init__(self, number: int, suit: PokerSuit):
        self.number = number
        self.suit = suit
        self.point = min(number + 1, 10)

    def __str__(self):
        return str(self.suit.value) + self._poker_name[self.number]

    def __eq__(self, other):
        if not isinstance(other, Poker):
            return False
        return self.point == other.point and self.suit == other.suit

    def __hash__(self):
        return hash(self._poker_name)


class BlackJackPlayer:
    client: Selector
    is_bookmaker: bool
    bet: int
    cards: list[Poker]
    bet_pair: bool
    has_split: bool
    can_operate: bool
    is_double: bool
    has_assurance: bool
    has_busted: bool
    has_surrendered: bool

    def __init__(self, player: Selector, bet: int = 0, is_bookmaker: bool = False):
        self.client = player
        self.is_bookmaker = is_bookmaker
        self.bet = bet
        self.cards = []
        self.bet_pair = False
        self.has_split = False
        self.can_operate = False
        self.is_double = False
        self.has_assurance = False
        self.has_busted = False
        self.has_surrendered = False

    def draw_card(self, *cards: Poker):
        self.cards.extend(cards)

    def calculate_point(self) -> int:
        return self.calculate_cards_point(*self.cards)

    @staticmethod
    def calculate_cards_point(*cards: Poker):
        point = 0
        for card in sorted(cards, key=lambda x: x.point, reverse=True):
            if card.point == 1:
                point += 11 if point <= 10 else 1
            else:
                point += card.point
        return point

    def can_double_bet(self) -> bool:
        if len(self.cards) != 2:
            return False
        return self.calculate_point() in [11, 21] and not self.is_double

    def can_split(self) -> bool:
        return False if len(self.cards) != 2 else self.cards[0] == self.cards[1]


class BlackJackData:
    def __init__(self, scene: Selector):
        self.scene = scene
        self.black_jack_players: dict[Selector, BlackJackPlayer] = {}
        self.phase: BlackJackPhase = BlackJackPhase.Callin
        self.card_number: int = 0
        self.card_pile: list[Poker] = []
        self.create_card_pile()
        self.shuffle_card_pile()

    def __eq__(self, other):
        return (
            False
            if isinstance(other, BlackJackData)
            else self.scene.pattern == other.scene.pattern
        )

    def __hash__(self):
        return hash(self.scene)

    def create_card_pile(self):
        for _, i in itertools.product(range(DECK_NUM), range(52)):
            number = i // 4
            suit = list(PokerSuit.__members__.values())[i % 4]
            card = Poker(number, suit)
            self.card_pile.append(card)
        self.shuffle_card_pile()

    def shuffle_card_pile(self):
        random.Random(datetime.now(timezone.utc).timestamp()).shuffle(self.card_pile)

    def bet(self, player: Selector, bet_num: int):
        self.black_jack_players.setdefault(
            player, BlackJackPlayer(player, bet=0)
        ).bet += bet_num

    def end_bet(self):
        self.phase = BlackJackPhase.Operation
        self.black_jack_players[BOOKMAKER_SELECTOR] = BlackJackPlayer(
            BOOKMAKER_SELECTOR, 0, True
        )  # 添加一位庄家
        for player in self.black_jack_players.values():
            player.draw_card(self.card_pile.pop(), self.card_pile.pop())
            player.can_operate = True

    def deal(self, player: Selector):
        player = self.black_jack_players[player]
        card = self.card_pile.pop()
        player.draw_card(card)
        return card, player.calculate_point() <= 21

    def assurance(self, player: Selector):
        if self.black_jack_players[BOOKMAKER_SELECTOR].cards[0].number == 0:
            self.black_jack_players[player].has_assurance = True
            return True
        return False

    def double_bet(self, player: Selector):
        player = self.black_jack_players[player]
        player.bet *= 2
        player.can_operate = False

    def fold(self, player: Selector):
        self.black_jack_players[player].can_operate = False

    def bet_pair(self, player: Selector):
        player = self.black_jack_players[player]
        if not player.bet_pair:
            player.bet_pair = True
            return True
        return False

    def split(self, player: Selector):
        player = self.black_jack_players[player]
        player.has_split = True
        player.can_operate = False
        piles = [[player.cards[0]], [player.cards[1]]]
        for pile in piles:
            while player.calculate_cards_point(*pile) < 17:
                poker = self.card_pile.pop()
                pile.append(poker)
        raw_cards = player.cards
        player.cards = piles
        return raw_cards, piles

    def surrender(self, player: Selector):
        self.black_jack_players[player].can_operate = False
        self.black_jack_players[player].has_surrendered = True

    def busted(self, player: Selector):
        player = self.black_jack_players[player]
        player.can_operate = False
        player.has_busted = True

    def check_all_fold(self):
        return not [
            player
            for player in self.black_jack_players.values()
            if player.client != BOOKMAKER_SELECTOR and player.can_operate
        ]

    def fold_all(self):
        for player in self.black_jack_players:
            self.fold(player)

    def bookmaker_operate(self):
        bookmaker = self.black_jack_players[BOOKMAKER_SELECTOR]
        while bookmaker.calculate_point() < 17:
            self.deal(BOOKMAKER_SELECTOR)
        msg = "庄家开的牌组是：\n"
        for card in bookmaker.cards:
            msg += f" {card}"
        return msg

    def check(self):
        return {
            player: int(self.calculate_bet(player))
            for player in self.black_jack_players
            if not self.black_jack_players[player].is_bookmaker
        }

    def calculate_bet(self, player: Selector):
        player = self.black_jack_players[player]
        coefficient = (
            (1 - int(player.has_assurance) * 0.5) * self.normal_point(player.client)
            + self.pair_point(player.client)
            + self.special_pattern_point(player.client)
            + int(player.has_assurance) * self.assurance_point(player.client)
        )
        return player.bet * coefficient

    def normal_point(self, player: Selector):
        player = self.black_jack_players[player]
        if player.has_surrendered:
            return 0.5
        if player.has_split:
            point_1 = player.calculate_cards_point(player.cards[0])
            if point_1 > 21:
                point_1 = 0
            point_2 = player.calculate_cards_point(player.cards[1])
            if point_2 > 21:
                point_2 = 0
            return self.compare_with_bookmaker(point_1) + self.compare_with_bookmaker(
                point_2
            )
        if player.has_busted:
            return 0
        return self.compare_with_bookmaker(player.calculate_point())

    def pair_point(self, player: Selector):
        player = self.black_jack_players[player]
        if not player.bet_pair:
            return 0
        bookmaker = self.black_jack_players[BOOKMAKER_SELECTOR]
        return 11 if bookmaker.cards[0] == bookmaker.cards[1] else 0

    def assurance_point(self, player: Selector):
        player = self.black_jack_players[player]
        if not player.has_assurance:
            return 0
        bookmaker = self.black_jack_players[BOOKMAKER_SELECTOR]
        return int(bookmaker.cards[1] == 10) * (1 + int(player.has_split))

    def special_pattern_point(self, player: Selector):
        player = self.black_jack_players[player]
        cards = player.cards
        if len(cards) != 3:
            return 0
        cards_point = [card.point for card in cards]
        if all(_ == 7 for _ in cards_point) or {6, 7, 8}.issubset(set(cards_point)):
            return 3
        return 0

    def compare_with_bookmaker(self, point):
        bookmaker = self.black_jack_players[BOOKMAKER_SELECTOR]
        bookmaker_point = bookmaker.calculate_point()
        if bookmaker_point > 21:
            bookmaker_point = 1
        if bookmaker_point > point:
            return 0
        elif bookmaker_point == point:
            return 1
        else:
            return 2
