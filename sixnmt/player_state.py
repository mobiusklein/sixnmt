import click
import random
from uuid import uuid4

try:
    raw_input
    input = raw_input
except:
    input = input


class BaseStrategy(object):
    def __init__(self, player_state=None, game_state=None, *args, **kwargs):
        self.player_state = player_state
        self.game_state = game_state

    def find_pile_for_card(self, card):
        number = card.card_number
        minimum_distance = float('inf')
        minimum_index = None

        for i, pile in enumerate(self.game_state.piles):
            if pile[-1].card_number < number:
                distance = number - pile[-1].card_number
                if distance < minimum_distance:
                    minimum_distance = distance
                    minimum_index = i
        if minimum_index is not None:
            return self.game_state.piles[minimum_index]
        else:
            return None

    def acquire_game_state(self, game_state):
        """Sets the GameState this object is tied to

        Parameters
        ----------
        game_state : game_state.GameState
            The game state to observe
        """
        self.game_state = game_state

    def select_card_to_play(self):
        """Chooses the card to be played this turn. Does not
        remove the card from the bound PlayerState's hand.

        This default behavior chooses the card at random. To make
        the strategy behave differently, overwrite this method.

        Returns
        -------
        Card
            The card to be played.
        """
        key = random.choice(tuple(self.player_state.hand.keys()))
        card = self.player_state.get_card(key)
        return card

    def play_card(self, card):
        """Plays the given card, removing it from the player hand and
        resolves all consequences such as picking up or replacing
        a pile.

        Parameters
        ----------
        card : deck.Card
            The card to be played
        """
        self.player_state.remove_played_card(card.card_number)
        self.game_state.play_card(card, self.player_state)

    def pickup_choice(self, piles):
        """Chooses the pile of cards to pick up when the player's
        move would cause a pile pickup choice to occur, such as when
        the player plays a card that is lower than every active pile.

        This method must return the index of the pile picked up, and
        the pile picked up. it also calls PlayerState.pickup_pile on
        the chosen pile, adding its contents to the bound player's
        bullpen.

        By default this method chooses the first pile with the fewest bulls.
        Override this method to change the player's behavior.

        Parameters
        ----------
        piles : list of game_state.Pile
            The current piles from the game state

        Returns
        -------
        int
            The index of the pile picked up
        game_state.Pile
            The pile picked up
        """
        i, pile = min(zip(range(len(piles)), piles), key=lambda x: x[1].running_bulls)
        self.player_state.pickup_pile(pile)
        return i, pile

    def new_round(self):
        """Signal that a new round has begun, and that any state carried in the
        Strategy instance should be cleared.
        """
        pass


class InteractivePlayerStrategy(BaseStrategy):
    def quit(self):
        click.secho("%s quit!" % self.player_state)
        import sys
        sys.exit()

    def select_card_to_play(self):
        """Allows a human player to interactively choose the card to play
        from the console.

        Returns
        -------
        deck.Card
        """
        for card in sorted(self.player_state.hand.values()):
            click.secho('\t%r' % card)
        card_number = input("Enter the card number to choose to play: ")
        if card_number == 'q':
            self.quit()
        if int(card_number) not in self.player_state.hand:
            click.secho("Card not found.")
            return self.select_card_to_play()
        else:
            card = self.player_state.hand[int(card_number)]
            pile = self.find_pile_for_card(card)
            if pile is None:
                return card
            else:
                if len(pile) == 5:
                    answer = input("Are you sure? That pile is full: y/n")
                    if answer.lower()[0] == 'y':
                        return card
                    else:
                        return self.select_card_to_play()
                else:
                    return card

        def pickup_choice(self, piles):
            for i, pile in enumerate(piles):
                click.secho("%d: %s" % (i, pile))
            pile_number = input("Enter the pile number to choose to pick up: ")
            if pile_number == 'q':
                self.quit()
            pile_number = int(pile_number)
            if pile_number not in range(len(piles)):
                click.secho("Pile not found")
                return self.pickup_choice(piles)
            else:
                pile = piles[pile_number]
                self.player_state.pickup_pile(pile)
                return pile_number, pile


class RuleBasedPlayerStrategy(BaseStrategy):
    def select_card_to_play(self):
        """Chooses the card to be played this turn. Does not
        remove the card from the bound PlayerState's hand.

        Returns
        -------
        Card
            The card to be played.
        """
        chosen_key = None

        smallest_delta = float('inf')
        smallest_delta_key = None

        unacceptable_options = set()

        for key in self.player_state.hand:
            for pile in self.game_state.piles:

                bad_move = len(pile) >= 4
                delta = key - pile.last.card_number
                if delta < 4 and bad_move:
                    unacceptable_options.add(key)
                    continue
                if delta < 0:
                    continue
                if delta < smallest_delta:
                    smallest_delta = delta
                    smallest_delta_key = key

        if smallest_delta < 4:
            chosen_key = smallest_delta_key
            card = self.player_state.get_card(chosen_key)
        else:
            card = super(RuleBasedPlayerStrategy, self).select_card_to_play()
            i = 0
            # Don't randomly shoot self in foot
            while card.card_number in unacceptable_options and i < 10:
                card = super(RuleBasedPlayerStrategy, self).select_card_to_play()
                i += 1
        return card


class PlayerState(object):
    def __init__(self, id=None, hand=None, bullpen=None, strategy=None):
        if id is None:
            id = uuid4().int
        if hand is None:
            hand = dict()
        if bullpen is None:
            bullpen = []
        if strategy is None:
            strategy = RuleBasedPlayerStrategy(self)
        self.id = id
        self.hand = hand
        self.bullpen = bullpen
        self.strategy = strategy
        self.running_bulls = sum(c.n_bulls for c in bullpen)

    def set_strategy(self, strategy):
        """Sets the strategy bound to this player to `strategy`,
        and updates all context references.

        Parameters
        ----------
        strategy : Strategy
        """
        old = self.strategy
        self.strategy = strategy
        if old.game_state is not None and strategy.game_state is None:
            strategy.game_state = old.game_state
        strategy.player_state = self

    def new_round(self):
        """Calls `self.strategy.new_round()`
        """
        self.strategy.new_round()

    def set_game_state(self, game_state):
        """Calls `self.strategy.acquire_game_state(game_state)`
        """
        self.strategy.acquire_game_state(game_state)

    def pickup_choice(self, piles):
        """Calls and returns `self.strategy.pickup_choice(piles)`
        and logs the event.
        """
        click.secho("%s choosing pile to pick up" % (self,), fg='yellow')
        i, pile = self.strategy.pickup_choice(piles)
        return i, pile

    def select_card_to_play(self):
        """Calls and returns `self.strategy.select_card_to_play()`
        and logs the event.
        """
        card = self.strategy.select_card_to_play()
        click.secho("%s revealed %s" % (self, card))
        return card

    def play_card(self, card):
        """Calls `self.strategy.play_card(card)`
        and logs the event.
        """
        self.strategy.play_card(card)

    def get_card(self, key):
        """Retrieves a card from `hand` by its card number

        Parameters
        ----------
        key : int
            The card number to fetch the card for

        Returns
        -------
        deck.Card
        """
        return self.hand[key]

    def pickup_pile(self, pile):
        click.secho("%s picked up %s" % (self, pile), fg='yellow' if pile.running_bulls < 5 else 'red')
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
