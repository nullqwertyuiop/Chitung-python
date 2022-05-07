import random
import time
from enum import Enum
from typing import List, Union

DECK_NUM = 4  # 四副牌


class BlackJackPhase(Enum):
    Callin = 0
    Bet = 1
    Operation = 2


class PokerSuit(Enum):
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
    _poker_name = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

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
    def __init__(self, player_id, bet=0, is_bookmaker=False):
        self.player_id = player_id
        self.is_bookmaker = is_bookmaker
        self.bet = bet
        self.cards: List[Poker] = []
        self.bet_pair: bool = False
        self.has_split: bool = False
        self.can_operate: bool = False
        self.is_double: bool = False
        self.has_assurance: bool = False
        self.has_busted: bool = False
        self.has_surrendered: bool = False

    def draw_card(self, cards: Union[Poker, List[Poker]]):
        if isinstance(cards, Poker):
            self.cards.append(cards)
        elif isinstance(cards, list):
            self.cards.extend(cards)

    def calculate_point(self) -> int:
        return self.calculate_cards_point(self.cards)

    @staticmethod
    def calculate_cards_point(cards: Union[List[Poker], Poker]):
        point = 0
        if isinstance(cards, Poker):
            cards = [cards]
        for card in sorted(cards, key=lambda x: -x.point):
            if card.point == 1:
                point += 11 if 11 + point <= 21 else 1
            else:
                point += card.point
        return point

    def can_double_bet(self) -> bool:
        if len(self.cards) != 2:
            return False
        # 两张牌情况下21点只可能是A+10，这种情况必然可以看成11点
        return self.calculate_point() in [11, 21] and not self.is_double

    def can_split(self) -> bool:
        if len(self.cards) != 2:
            return False
        return self.cards[0] == self.cards[1]


class BlackJackData:
    def __init__(self, game_id):
        self.id = game_id
        self.black_jack_players: List[BlackJackPlayer] = []
        self.phase: BlackJackPhase = BlackJackPhase.Callin
        self.card_number: int = 0
        self.card_pile: List[Poker] = []
        self.create_card_pile()
        self.shuffle_card_pile()

    def __eq__(self, other):
        if isinstance(other, BlackJackData):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def create_card_pile(self):
        for _ in range(DECK_NUM):
            for i in range(52):
                number = i // 4
                suit = PokerSuit.get(i % 4)
                card = Poker(number, suit)
                self.card_pile.append(card)
        self.shuffle_card_pile()

    def shuffle_card_pile(self):
        random.Random(time.time().real).shuffle(self.card_pile)

    def bet(self, player_id, bet_num):
        player = self.get_player(player_id)
        if player not in self.black_jack_players:
            self.black_jack_players.append(BlackJackPlayer(player_id, bet=bet_num))
        else:
            self.get_player(player_id).bet += bet_num

    def end_bet(self):
        """
        结束下注，给所有下注玩家发两张牌
        """
        self.phase = BlackJackPhase.Operation
        self.black_jack_players.append(BlackJackPlayer(0, 0, True))  # 添加一位庄家
        for player in self.black_jack_players:
            player.draw_card([self.card_pile.pop(), self.card_pile.pop()])
        self.phase = BlackJackPhase.Operation
        for p in self.black_jack_players:
            p.can_operate = True

    def get_player(self, player_id):
        res = [p for p in self.black_jack_players if p.player_id == player_id]
        if len(res) != 1:
            return None
        return res[0]

    def deal(self, player_id):
        """加牌，爆牌输出(抽到的牌，爆牌了吗)"""
        player = self.get_player(player_id)
        card = self.card_pile.pop()
        player.draw_card(card)
        return card, player.calculate_point() <= 21

    def assurance(self, player_id):
        """买保险"""
        if self.get_player(0).cards[0].number == 0:  # A的序号是0
            self.get_player(player_id).has_assurance = True
            return True
        return False

    def double_bet(self, player_id):
        """双倍下注"""
        player = self.get_player(player_id)
        player.bet *= 2
        player.can_operate = False

    def fold(self, player_id):
        """停牌"""
        self.get_player(player_id).can_operate = False

    def bet_pair(self, player_id):
        """下注对子"""
        player = self.get_player(player_id)
        if not player.bet_pair:
            player.bet_pair = True
            return True
        return False

    def split(self, player_id):
        """分牌"""
        player = self.get_player(player_id)
        player.has_split = True
        player.can_operate = False
        piles = [[player.cards[0]], [player.cards[1]]]  # 分成两个牌堆
        for pile in piles:
            while player.calculate_cards_point(pile) < 17:
                poker = self.card_pile.pop()
                pile.append(poker)
        raw_cards = player.cards
        player.cards = piles
        return raw_cards, piles

    def surrender(self, player_id):
        """投降"""
        self.get_player(player_id).can_operate = False
        self.get_player(player_id).has_surrendered = True

    def busted(self, player_id):
        player = self.get_player(player_id)
        player.can_operate = False
        player.has_busted = True

    def check_all_fold(self):
        return (
            len(
                [
                    player
                    for player in self.black_jack_players
                    if player.player_id != 0 and player.can_operate
                ]
            )
            == 0
        )

    def fold_all(self):
        for p in self.black_jack_players:
            self.fold(p.player_id)

    def bookmaker_operate(self):
        bookmaker = self.get_player(0)
        while bookmaker.calculate_point() < 17:
            self.deal(0)
        msg = "庄家开的牌组是：\n"
        for card in bookmaker.cards:
            msg += f" {card}"
        return msg

    def check(self):
        result = {}
        for p in self.black_jack_players:
            if p.is_bookmaker:
                continue
            result[p.player_id] = self.calculate_bet(p.player_id)
        return result

    def calculate_bet(self, player_id):
        """计算赌局结果"""
        player = self.get_player(player_id)
        coefficient = (
            (1 - int(player.has_assurance) * 0.5) * self.normal_point(player_id)
            + self.pair_point(player_id)
            + self.special_pattern_point(player_id)
            + int(player.has_assurance) * self.assurance_point(player_id)
        )
        return player.bet * coefficient

    def normal_point(self, player_id):
        """计算得分"""
        player = self.get_player(player_id)
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

    def pair_point(self, player_id):
        player = self.get_player(player_id)
        bookmaker = self.get_player(0)
        if not player.bet_pair:
            return 0
        return 11 if bookmaker.cards[0] == bookmaker.cards[1] else 0

    def assurance_point(self, player_id):
        player = self.get_player(player_id)
        bookmaker = self.get_player(0)
        if not player.has_assurance:
            return 0
        return int(bookmaker.cards[1] == 10) * (1 + int(player.has_split))

    def special_pattern_point(self, player_id):
        player = self.get_player(player_id)
        cards = player.cards
        if len(cards) != 3:
            return 0
        cards_point = [card.point for card in cards]
        if all(_ == 7 for _ in cards_point) or {6, 7, 8}.issubset(set(cards_point)):
            return 3
        return 0

    def compare_with_bookmaker(self, point):
        bookmaker = self.get_player(0)
        bookmaker_point = bookmaker.calculate_point()
        if bookmaker_point > 21:
            bookmaker_point = 1
        if bookmaker_point > point:
            return 0
        elif bookmaker_point == point:
            return 1
        else:
            return 2
