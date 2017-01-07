from collections import namedtuple

ScoreCell = namedtuple('ScoreCell', ['score', 'value'])


def binsearch(array, value):
    lo = 0
    hi = len(array) - 1

    while hi - lo:
        i = (hi + lo) / 2
        x = array[i]
        if x == value:
            return i
        elif hi - lo == 1:
            return i
        elif x < value:
            lo = i
        elif x > value:
            hi = i
    return i


class NearestValueLookUp(object):
    def __init__(self, items):
        if isinstance(items, dict):
            items = items.items()
        self.items = sorted([ScoreCell(*x) for x in items], key=lambda x: x[0])

    def _find_closest_item(self, value):
        array = self.items
        lo = 0
        hi = len(array) - 1

        while hi - lo:
            i = (hi + lo) / 2
            x = array[i][0]
            if x == value:
                return i
            elif (hi - lo) == 1:
                return i
            elif x < value:
                lo = i
            elif x > value:
                hi = i

    def get_pair(self, key):
        return self.items[self._find_closest_item(key) + 1]

    def __getitem__(self, key):
        ix = self._find_closest_item(key)
        ix += 1
        pair = self.items[ix]
        if pair[0] < key:
            return 0
        return pair[1]
