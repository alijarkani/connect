import random
from player import Player
from game import Game
from board import Board


class CrazyAI(Player):
    def __init__(self, title, color):
        """Random AI player"""
        super().__init__(title, color)

    def play(self, board: Board):
        while board.has_empty_cell:
            row = random.randint(0, board.size - 1)
            col = random.randint(0, board.size - 1)

            if board.is_empty((row, col)):
                yield row, col


