from board import GUIBoard, Board
from game import Game
from player import Human, WHITE, BLACK, BLUE, RED, GREEN
from bots.crazy import CrazyAI

players = [
    Human('Human', WHITE),
    CrazyAI('One', BLACK),
    CrazyAI('Two', BLUE),
    CrazyAI('Three', RED),
    CrazyAI('Four', GREEN),
]


if __name__ == '__main__':
    board = GUIBoard(size=12)
    game = Game(board, players, shuffle_players=False)
    game.handle()

