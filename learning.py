# https://www.youtube.com/watch?v=cO5g5qLrLSo
# https://www.youtube.com/watch?v=bD6V3rcr_54


import random
import numpy as np
from os.path import exists
from gym import Env
from gym.spaces import Discrete, Box
from board import Board, GUIBoard
from player import Player, WHITE, BLACK
from bots.ann import ANN
from bots.crazy import CrazyAI
from keras.models import Sequential, load_model
from keras.layers import Dense, Flatten, Conv2D, Input, Reshape
from keras.optimizers import Adam
from rl.agents import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory
from typing import Optional


GUI = True
SIZE = 13
WIN = 6


class ConnectEnv(Env):
    def __init__(self):
        self.me = Player('Me', WHITE)
        self.rival = ANN('Rival', BLACK) if exists('bots/ann.h5') else CrazyAI('Rival', BLACK)
        if GUI:
            self.board = GUIBoard(size=SIZE)
            self.board.draw()
        else:
            self.board = Board(size=SIZE)

        self.action_space = Discrete(SIZE * SIZE)
        self.observation_space = Box(low=0, high=1, shape=(SIZE, SIZE, 2))
        self.state = self.get_state()


    def get_state(self):
        state = np.zeros((SIZE, SIZE, 2), dtype=int)
        for r, row in enumerate(self.board.map):
            for c, cell in enumerate(row):
                if cell is not None:
                    key = 0 if cell.owner == self.me else 1
                    state[r, c, key] = 1

        return state


    def calc_reward(self):
        reward = 0
        done = not self.board.has_empty_cell
        for x, y in self.board.utils.get_every_lines_indexes():
            parts = self.board.utils.line_partition(x, y)
            for i, part in enumerate(parts):
                if part.player is not None:
                    if part.count >= WIN:
                        done = True

                    right = 0
                    left = 0
                    for k in range(i - 1, -1, -1):
                        if parts[k].player is not None and parts[k].player != part.player:
                            break
                        left += parts[k].count

                    for k in range(i + 1, len(parts)):
                        if parts[k].player is not None and parts[k].player != part.player:
                            break
                        right += parts[k].count

                    c = max(0, part.count + min(right, WIN - 1) + min(left, WIN - 1) - WIN)
                    reward += part.count ** 2 * (1 if part.player == self.me else -1) * c

        return reward, done

    def step(self, action):
        row = action // SIZE
        col = action % SIZE
        was_empty = self.board.is_empty((row, col))
        self.board.put_stone((row, col), self.me)

        if self.board.has_empty_cell:
            row, col = self.rival.play(self.board).__next__()
            self.board.put_stone((row, col), self.rival)

        reward, done = self.calc_reward()
        info = {}

        if not was_empty and self.board.has_empty_cell:
            reward = min(-100, reward)
            empty_cells = np.where((self.board.map == None).reshape(-1))[0]
            rival_action = random.choice(empty_cells)
            row = rival_action // SIZE
            col = rival_action % SIZE
            self.board.put_stone((row, col), self.me)

        return self.state, reward, done, info

    def reset(self, *, seed: Optional[int] = None, return_info: bool = False, options: Optional[dict] = None):
        if GUI:
            self.board = GUIBoard(size=SIZE)
            self.board.draw()
        else:
            self.board = Board(size=SIZE)

        self.state = self.get_state()
        return self.state


def build_model():
    model = Sequential()
    model.add(Input((1, SIZE, SIZE, 2)))
    model.add(Conv2D(32, (3, 3), activation='relu'))
    model.add(Conv2D(32, (3, 3), activation='relu'))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(Conv2D(128, (3, 3), activation='relu'))
    model.add(Flatten())
    model.add(Dense(256, activation='relu'))
    model.add(Dense(256, activation='relu'))
    model.add(Dense(SIZE * SIZE, activation='linear'))
    model.summary()
    return model


if __name__ == '__main__':
    env = ConnectEnv()

    model = load_model('bots/ann.h5') if exists('bots/ann.h5') else build_model()
    policy = BoltzmannQPolicy()
    memory = SequentialMemory(limit=250000, window_length=1)
    dqn = DQNAgent(model=model, memory=memory, policy=policy,
                   nb_actions=SIZE * SIZE, nb_steps_warmup=10, target_model_update=1e-2)

    dqn.compile(Adam(lr=1e-3), metrics=['mse'])
    dqn.fit(env, nb_steps=250000, visualize=False, verbose=1)
    model.save('bots/ann.h5')
    print('Done')
