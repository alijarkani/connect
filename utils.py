import numpy as np


class Partition(object):
    def __init__(self, player, count, start_index, end_index, start, end):
        """
        Represent cells in the vicinity along a line that has a same owner
        """
        self._player = player
        self._count = count
        self._start_index = start_index
        self._end_index = end_index
        self._start = start
        self._end = end

    @property
    def player(self):
        return self._player

    @property
    def count(self):
        return self._count

    @property
    def start_index(self):
        return self._start_index

    @property
    def end_index(self):
        return self._end_index

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end


class Utils(object):
    def __init__(self, size, board_map):
        self.size = size
        self.map = board_map

    def line_partition(self, x, y):
        line = self.map[x, y]
        parts = []
        player = None
        count = 0
        start = 0
        start_point = x[0], y[0]
        for i, stone in enumerate(line):
            owner = stone.owner if stone is not None else None
            if owner == player:
                count += 1
            else:
                if count:
                    parts.append(Partition(player, count, start, i - 1, start_point, (x[i-1], y[i-1])))

                player = owner
                count = 1
                start = i
                start_point = x[i], y[i]

        if count:
            parts.append(Partition(player, count, start, len(line) - 1, start_point, (x[-1], y[-1])))

        return parts

    def get_rows_indexes(self):
        for i in range(self.size):
            yield i * np.ones(self.size, dtype=int), np.arange(0, self.size)

    def get_cols_indexes(self):
        for i in range(self.size):
            yield np.arange(0, self.size), i * np.ones(self.size, dtype=int)

    def get_ascending_line_indexes(self):
        for i in range(-self.size + 1, self.size):
            x = np.arange(max(0, i), min(self.size, i + self.size))
            y = np.flip(x)
            yield x, y

    def get_descending_line_indexes(self):
        for i in range(-self.size + 1, self.size):
            x = np.arange(max(0, i), min(self.size, i + self.size))
            y = self.size - np.flip(x) - 1
            yield x, y

    def get_every_lines_indexes(self, cross_point=None):
        if cross_point:
            row, col = cross_point

            yield row * np.ones(self.size, dtype=int), np.arange(0, self.size)
            yield np.arange(0, self.size), col * np.ones(self.size, dtype=int)

            total = row + col + 1
            sub = row - col

            x = np.arange(max(0, total - self.size), min(self.size, total))
            y = np.flip(x)
            yield x, y

            x = np.arange(max(0, sub), min(self.size, sub + self.size))
            y = self.size - np.flip(x) - 1
            yield x, y

        else:

            for x, y in self.get_rows_indexes():
                yield x, y

            for x, y in self.get_cols_indexes():
                yield x, y

            for x, y in self.get_ascending_line_indexes():
                yield x, y

            for x, y in self.get_descending_line_indexes():
                yield x, y
