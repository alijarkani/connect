import random
from player import Player
from game import Game
from board import Board


class CrazyAI(Player):
    def __init__(self, title, color):
        """A human player logic"""
        super().__init__(title, color)

    def play(self, board: Board, game: Game, me: Player):
        while True:
            row = random.randint(0, board.size - 1)
            col = random.randint(0, board.size - 1)

            if board.is_empty((row, col)):
                yield row, col


