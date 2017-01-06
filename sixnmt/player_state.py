import random
from uuid import uuid4


class BaseStrategy(object):
    def __init__(self, player_state, game_state=None, *args, **kwargs):
        self.player_state = player_state
        self.game_state = game_state

    def acquire_game_state(self, game_state):
        self.game_state = game_state

    def select_card_to_play(self):
        key = random.choice(tuple(self.player_state.hand.keys()))
        card = self.player_state.get_card(key)
        return card

    def play_card(self, card):
        self.player_state.remove_played_card(card.card_number)
        self.game_state.play_card(card, self.player_state)

    def pickup_choice(self, piles):
        i, pile = min(zip(range(len(piles)), piles), key=lambda x: x[1].running_bulls)
        self.player_state.pickup_pile(pile)
        return i, pile

    def new_round(self):
        pass


class PlayerState(object):
    def __init__(self, id=None, hand=None, bullpen=None, strategy=None):
        if id is None:
            id = uuid4().int
        if hand is None:
            hand = dict()
        if bullpen is None:
            bullpen = []
        if strategy is None:
            strategy = BaseStrategy(self)
        self.id = id
        self.hand = hand
        self.bullpen = bullpen
        self.strategy = strategy
        self.running_bulls = sum(c.n_bulls for c in bullpen)

    def set_strategy(self, strategy):
        old = self.strategy
        self.strategy = strategy
        if old.game_state is not None and strategy.game_state is None:
            strategy.game_state = old.game_state
        strategy.player_state = self

    def new_round(self):
        self.strategy.new_round()

    def set_game_state(self, game_state):
        self.strategy.acquire_game_state(game_state)

    def pickup_choice(self, piles):
        print("%s choosing pile to pick up" % (self,))
        i, pile = self.strategy.pickup_choice(piles)
        return i, pile

    def select_card_to_play(self):
        card = self.strategy.select_card_to_play()
        print("%s revealed %r" % (self, card))
        return card

    def play_card(self, card):
        self.strategy.play_card(card)

    def get_card(self, key):
        return self.hand[key]

    def pickup_pile(self, pile):
        print("%s picked up %r (%d bulls)" % (self, pile, pile.running_bulls))
        self.running_bulls += pile.running_bulls
        self.bullpen.extend(pile)

    def remove_played_card(self, card_number):
        return self.hand.pop(card_number)

    def __repr__(self):
        return "PlayerState(%r|%d, %d)" % (self.id, len(self.hand), self.running_bulls)

    def fill_hand(self, cards):
        self.hand = dict()
        for card in cards:
            self.hand[card.card_number] = card
