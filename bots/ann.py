import numpy as np
from player import Player
from board import Board
from keras.models import load_model

SIZE = 13


class ANN(Player):
    def __init__(self, title, color):
        """Random AI player"""
        super().__init__(title, color)
        self.model = load_model('bots/ann.h5')

    def get_state(self, board):
        state = np.zeros((SIZE, SIZE, 2), dtype=int)
        for r, row in enumerate(board.map):
            for c, cell in enumerate(row):
                if cell is not None:
                    key = 0 if cell.owner == self else 1
                    state[r, c, key] = 1

        return state

    def play(self, board: Board):
        state = self.get_state(board).reshape((1, 1, SIZE, SIZE, 2))
        heatmap = self.model.predict(state, verbose=0).reshape(-1)

        while board.has_empty_cell:
            action = heatmap.argmax()
            row = action // SIZE
            col = action % SIZE

            while not board.is_empty((row, col)):
                heatmap[action] = -np.Inf
                action = heatmap.argmax()
                row = action // SIZE
                col = action % SIZE

            yield row, col
