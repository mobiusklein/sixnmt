from functools import total_ordering


@total_ordering
class Card(object):
    def __init__(self, card_number, n_bulls=None):
        if n_bulls is None:
            n_bulls = self.compute_bulls(card_number)
        self.card_number = card_number
        self.n_bulls = n_bulls

    def __repr__(self):
        return "Card(%d, %d)" % (self.card_number, self.n_bulls)

    @staticmethod
    def compute_bulls(number):
        if number % 11 == 0 and number % 5 == 0:
            return 7
        elif number % 11 == 0:
            return 5
        elif number % 10 == 0:
            return 3
        elif number % 5 == 0:
            return 2
        else:
            return 1

    def __lt__(self, other):
        return self.card_number < other.card_number


def make_deck(n_players):
    total = 4 + 10 * n_players
    return [Card(i) for i in range(1, total + 1)]
