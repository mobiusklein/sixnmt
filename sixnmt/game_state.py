import random

from deck import Card, make_deck
from player_state import PlayerState


class Pile(object):
    def __init__(self, cards):
        self.cards = list(cards)
        self.running_bulls = sum(c.n_bulls for c in self.cards)

    def add_card(self, card):
        self.cards.append(card)
        self.running_bulls += card.n_bulls

    def reset(self):
        self.cards = []
        self.running_bulls = 0

    def __iter__(self):
        return iter(self.cards)

    def __len__(self):
        return len(self.cards)

    def __repr__(self):
        return "Pile(%s)" % (repr(self.cards),)

    def __getitem__(self, i):
        return self.cards[i]


class TurnState(object):
    def __init__(self, game_state):
        self.game_state = game_state

    def play(self):
        players = self.game_state.players
        players_ordered = sorted(zip(
            players,
            [p.select_card_to_play() for p in players]
        ), key=lambda x: x[1].card_number)
        print('-' * 5)
        for player, card in players_ordered:
            player.play_card(card)


class GameState(object):
    def __init__(self, n_players, piles=None):
        if piles is None:
            piles = []
        self.n_players = n_players
        self.piles = piles

        self.players = [PlayerState(i) for i in range(n_players)]
        for player in self.players:
            player.set_game_state(self)

    def deal_hands(self):
        cards = make_deck(self.n_players)
        random.shuffle(cards)
        self.piles = [Pile([c]) for c in cards[:4]]
        i = 4
        n_cards_per_player = 10
        for player in self.players:
            player.new_round()
            player.fill_hand(cards[i:(i + n_cards_per_player)])
            i += n_cards_per_player

    def play_card(self, card, player=None):
        number = card.card_number
        minimum_distance = float('inf')
        minimum_index = None
        for i, pile in enumerate(self.piles):
            if pile[-1].card_number < number:
                distance = number - pile[-1].card_number
                if distance < minimum_distance:
                    minimum_distance = distance
                    minimum_index = i
        if minimum_index is None:
            i, pile = player.pickup_choice(self.piles)
            self.piles[i] = Pile([card])
        else:
            pile = self.piles[minimum_index]
            print("%s played %r on %r" % (player, card, pile))
            if len(pile) >= 5:
                player.pickup_pile(pile)
                pile.reset()
            pile.add_card(card)

    def play_turn(self):
        turn = TurnState(self)
        turn.play()

    def play_round(self):
        has_cards = True
        while has_cards:
            print("=" * 10)
            self.play_turn()
            self.display_piles()
            print("")
            self.display_players()
            print("")
            if len(self.players[0].hand) == 0:
                has_cards = False

    def play_game(self):
        keep_going = True
        while keep_going:
            self.deal_hands()
            self.play_round()
            keep_going = not any(player.running_bulls > 77 for player in self.players)

    def display_piles(self):
        print("Piles:")
        for pile in self.piles:
            print("\t%r" % (pile,))

    def display_players(self):
        print("Players:")
        for player in self.players:
            print("\t%r" % (player,))
