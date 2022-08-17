import numpy as np
from abc import abstractmethod
from board import Board, GUIBoard
from game import Game
from typing import Generator, Tuple, Any

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)


class Player(object):
    def __init__(self, title: str, color: tuple):
        """
        Each player (human or AI) in the game has to be a Player instance
        """
        self._title = title
        self._border_color = color
        self._color = tuple(np.round((7 * np.array(color) + 3 * np.array((127, 127, 127))) / 10).astype(int))
        self._is_ai = True
        self._rivals = []

    def prepare(self, board: Board, game: Game):
        count = len(game.players)
        idx = game.players.index(self)
        for i in range(idx + 1, idx + count):
            self._rivals.append(game.players[i % count])

    @property
    def rivals(self):
        return self._rivals


    @property
    def title(self):
        return self._title

    @property
    def border_color(self):
        return self._border_color

    @property
    def color(self):
        return self._color

    @property
    def is_ai(self):
        return self._is_ai

    @abstractmethod
    def play(self, board: Board) -> Generator[Tuple[int, int], Any, None]:
        """
        The player should decide its action here,
        it can either return an array of coordinates or yield each coordinate separately
        """
        pass


class Human(Player):
    def __init__(self, title, color):
        """
        A human player logic
        """
        super().__init__(title, color)
        self._is_ai = False

    def show_map(self, board_map, size):
        """
        This method is only used when board doesn't have GUI
        """
        line = '    '
        for i in range(size):
            line += str(i % 10) + ' '
        print(line)
        print('   ' + '-' * (size * 2))
        for i, row in enumerate(board_map):
            line = str(i % 10) + ' | '
            for cell in row:
                line += '.' if cell is None else cell.owner.title[0]
                line += ' '
            print(line)

    def play(self, board: Board):
        """
        This is a human player instance. If the board supported GUI input it'll use it
        otherwise, it'll use numeric input
        """
        if isinstance(board, GUIBoard):
            for point in board.wait_for_click():
                yield point
        else:
            while True:
                self.show_map(board.map, board.size)

                x = int(input('row: '))
                y = int(input('col: '))
                if not board.is_valid((x, y)):
                    print('This cell is not valid')
                elif not board.is_empty((x, y)):
                    print('This cell is not empty')
                else:
                    yield x, y

