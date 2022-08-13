import numpy as np
import pygame
import math
import time
from stone import Stone
from utils import Utils
from typing import Optional, List

BOX_SIZE = 40
BOARD_PADDING = 45
BOTTOM_SIZE = 60


class Board(object):
    def __init__(self, size):
        """
        It's a basic board of the game. It contains map that is List[List[Optional[Stone]]] and store state of the game.
        """
        self._size = size
        self._empty_count = size * size
        self._map = np.empty((size, size), dtype=object)
        self._utils = Utils(size, self._map)
        self._history = []

    def get(self, x, y) -> Optional[Stone]:
        return self.map[x, y]

    @property
    def utils(self):
        return self._utils

    @property
    def history(self) -> List[Stone]:
        return self._history

    @property
    def size(self):
        return self._size

    @property
    def map(self):
        return self._map

    @property
    def has_empty_cell(self):
        return self._empty_count > 0

    def is_valid(self, point):
        row, col = point
        return 0 <= row < self._size and 0 <= col < self._size

    def is_empty(self, point):
        row, col = point
        return self._map[row, col] is None

    def draw(self):
        pass

    def rest(self, delay):
        pass

    def put_stone(self, point: tuple, player):
        """
        When a player made action then this is where the stone is placed on the board
        :param point: Tuple[int, int]
        :param player: Player
        :return: bool
        """
        if not point or not self.is_empty(point):
            return False

        self._empty_count -= 1
        stone = Stone(owner=player, pos=point)
        self._map[point] = stone
        self._history.append(stone)
        print(player.title, 'put a stone at ', point)
        return True

    def get_max_partition(self, player, cross_point=None):
        max_count = 0
        max_part = None

        for x, y in self.utils.get_every_lines_indexes(cross_point):
            parts = self.utils.line_partition(x, y)
            for part in parts:
                if part.player == player and part.count > max_count:
                    max_count = part.count
                    max_part = part

        return max_part

    def show_winner(self, player, partition):
        print(player.title + ' win')

    def show_draw(self):
        print('DRAW')

    def show_message(self, message):
        print(message)


class GUIBoard(Board):
    def __init__(self, size, background='wood.jpg'):
        """
        It's a graphical user interface including show the board with squares and show stones with circles,
        it also can detect mouse click on board
        """
        super().__init__(size)

        pygame.init()
        pygame.display.set_caption('Game')

        self._board_size = 2 * BOARD_PADDING + (self._size - 1) * BOX_SIZE
        self._screen = pygame.display.set_mode((self._board_size, self._board_size + BOTTOM_SIZE), 0, 32)
        self._background = pygame.image.load('images/' + background).convert()
        self._outline = pygame.Rect(BOARD_PADDING, BOARD_PADDING, BOX_SIZE * (size - 1), BOX_SIZE * (size - 1))

    def draw(self):
        pygame.draw.rect(self._background, (0, 0, 0), self._outline, width=3)
        self._outline.inflate_ip(20, 20)

        for i in range(self._size - 1):
            for j in range(self._size - 1):
                rect = pygame.Rect(BOARD_PADDING + (BOX_SIZE * i), BOARD_PADDING + (BOX_SIZE * j), BOX_SIZE, BOX_SIZE)
                pygame.draw.rect(self._background, (0, 0, 0), rect, 1)

        dots = math.floor((self._size - 2) / 3)
        for i in range(dots):
            for j in range(dots):
                coords = (
                    BOARD_PADDING + BOX_SIZE * 3 + (BOX_SIZE * 3 * i),
                    BOARD_PADDING + BOX_SIZE * 3 + (BOX_SIZE * 3 * j))
                pygame.draw.circle(self._background, (0, 0, 0), coords, 5, 0)
        self._screen.blit(self._background, (0, 0))

        pygame.display.update()
        pygame.time.wait(250)
        pygame.event.get()

    def put_stone(self, point, player):
        result = super().put_stone(point, player)
        if result:
            row, col = point
            coords = (col * BOX_SIZE + BOARD_PADDING, row * BOX_SIZE + BOARD_PADDING)
            pygame.draw.circle(self._screen, player.border_color, coords, int(BOX_SIZE / 2) - 3, 0)
            pygame.draw.circle(self._screen, player.color, coords, int(BOX_SIZE / 2) - 7, 0)
            pygame.display.update()

        return result

    def rest(self, delay):
        pygame.time.wait(int(delay * 100))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print('Program closed')
                exit()
        time.sleep(delay)

    def wait_for_click(self):
        while True:
            pygame.time.wait(250)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    point = self.transform(event)
                    if point and self.is_empty(point):
                        yield point

    def transform(self, event):
        if event.button == 1 and self._outline.collidepoint(event.pos):
            col = round((event.pos[0] - BOARD_PADDING) / BOX_SIZE)
            row = round((event.pos[1] - BOARD_PADDING) / BOX_SIZE)
            return min(self._size, max(0, row)), min(self._size, max(0, col))

    def show_winner(self, player, partition):
        x, y = partition.start_stone.pos
        start = (y * BOX_SIZE + BOARD_PADDING, x * BOX_SIZE + BOARD_PADDING)

        x, y = partition.end_stone.pos
        end = (y * BOX_SIZE + BOARD_PADDING, x * BOX_SIZE + BOARD_PADDING)
        pygame.draw.line(self._screen, (0, 255, 0), start, end, 5)
        pygame.display.update()

        self.show_message(player.title + ' win')

    def show_draw(self):
        self.show_message('DRAW')

    def show_message(self, message):
        top = self._board_size - 25
        blit_coords = (0, top)
        area_rect = pygame.Rect(blit_coords, (self._board_size, 70))
        self._screen.blit(self._background, blit_coords, area_rect)

        font = pygame.font.Font('fonts/Chalkduster.ttf', 64)
        img = font.render(message, True, (0, 0, 0))
        self._screen.blit(img, ((self._board_size - img.get_width()) / 2, top))
        pygame.display.update()
        super().show_message(message)
