import random
import numpy as np
from collections import deque
from player import Player
from game import Game
from board import Board
from typing import Optional, List
from stone import Stone


class Greedy(Player):
    def __init__(self, title, color):
        """Greedy AI player"""
        super().__init__(title, color)
        self.stone_each_turn = 2
        self.win = 6
        self.size = 13
        self.scores = np.zeros((13, 13))

    def prepare(self, board: Board, game: Game):
        super().prepare(board, game)
        self.win = game.win
        self.size = board.size
        self.scores = np.zeros((board.size, board.size))
        self.stone_each_turn = game.stone_each_turn


    def max_possibilities(self, line: List[Optional[Stone]], player: Player, stone_counts: int, return_all: bool = False):
        start_range = 0
        remains = stone_counts
        fill_cells = deque()
        actions = deque()

        for j, cell in enumerate(line):
            if cell is None:
                if remains > 0:
                    remains -= 1
                else:
                    actions.append((j - start_range, fill_cells.copy(), stone_counts))
                    start_range = fill_cells.popleft() + 1

                fill_cells.append(j)

            elif cell.owner != player:
                if len(fill_cells):
                    actions.append((j - start_range, fill_cells.copy(), stone_counts - remains))

                fill_cells.clear()
                start_range = j + 1
                remains = stone_counts

        if len(fill_cells):
            actions.append((len(line) - start_range, fill_cells.copy(), stone_counts - remains))


        if return_all:
            return actions

        if len(actions):
            max_len, _, _ = max(actions, key=lambda x: x[0])
            max_action = filter(lambda x: x[0] == max_len, actions)
            max_action = map(lambda x: list(x[1]), max_action)
            return max_len, list(max_action)

        return 0, []


    def play(self, board: Board):
        self.scores[:, :] = np.random.normal(size=(self.size, self.size)) - 3

        for x, y in board.utils.get_every_lines_indexes():
            if len(x) >= self.win:
                self.scores[x, y] += 1
                max_len, actions = self.max_possibilities(board.map[x, y], self, self.stone_each_turn)

                if max_len >= self.win:
                    for point in actions[0]:
                        yield x[point], y[point]

                actions = self.max_possibilities(board.map[x, y], self, self.win - 1, return_all=True)
                for max_len, points, stone_used in actions:
                    vicinity_count = max_len - stone_used
                    if vicinity_count > 0:
                        self.scores[x[points], y[points]] += vicinity_count


                for rival in self._rivals:
                    max_len, actions = self.max_possibilities(board.map[x, y], rival, self.stone_each_turn)

                    while max_len >= self.win:
                        acts = np.array(actions).reshape(-1)
                        unique, counts = np.unique(acts, return_counts=True)
                        point = unique[counts.argmax()]
                        yield x[point], y[point]

                        max_len, actions = self.max_possibilities(board.map[x, y], rival, self.stone_each_turn)


                    actions = self.max_possibilities(board.map[x, y], rival, self.win - 2, return_all=True)
                    for max_len, points, stone_used in actions:
                        vicinity_count = max_len - stone_used
                        if vicinity_count > 0:
                            self.scores[x[points], y[points]] += vicinity_count


        while board.has_empty_cell:
            max_index = self.scores.argmax()
            row = max_index // self.size
            col = max_index % self.size
            self.scores[row, col] = -np.Inf
            if board.is_empty((row, col)):
                yield row, col





