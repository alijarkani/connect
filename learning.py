# https://www.youtube.com/watch?v=cO5g5qLrLSo
# https://www.youtube.com/watch?v=bD6V3rcr_54

import os
import random
import numpy as np
from os.path import exists
from gym import Env
from gym.spaces import Discrete, Box
from board import Board, GUIBoard
from player import Player, WHITE, BLACK
from bots.ann import ANN
from bots.greedy import Greedy
from keras.models import Sequential, load_model, Model
from keras.layers import Dense, Flatten, Conv2D, Input, Reshape, Concatenate
from keras.optimizers import Adam
from rl.agents import DQNAgent
from rl.policy import BoltzmannQPolicy, GreedyQPolicy
from rl.memory import SequentialMemory
from typing import Optional

GUI = True
SIZE = 13
WIN = 6
STONE_TURN = 2


class ConnectEnv(Env):
    def __init__(self):
        self.last_result = "Start"
        self.me = Player('Me', WHITE)
        self.rival = Greedy('Rival', BLACK)
        if GUI:
            os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 0)
            self.board = GUIBoard(size=SIZE)
            self.board.draw()
        else:
            self.board = Board(size=SIZE)

        self.action_space = Discrete(SIZE * SIZE)
        self.observation_space = Box(low=0, high=1, shape=(SIZE, SIZE, 2))
        self.last_reward = 0

        rival_row, rival_col = self.rival.play(self.board).__next__()
        self.board.put_stone((rival_row, rival_col), self.rival)
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
        win = False
        for x, y in self.board.utils.get_every_lines_indexes():
            parts = self.board.utils.line_partition(x, y)
            for i, part in enumerate(parts):
                if part.player is not None:
                    if part.count >= WIN:
                        done = True
                        win = part.player == self.me
                    elif part.player != self.me and part.count >= WIN - STONE_TURN + 1:
                        done = (
                                    i - 1 >= 0 and
                                    parts[i - 1].player is None and
                                    parts[i - 1].count >= WIN - part.count
                               ) or (
                                    i + 1 < len(parts) and
                                    parts[i + 1].player is None and
                                    parts[i + 1].count >= WIN - part.count
                               )

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
                    reward += part.count ** 2 * (2 if part.player == self.me else -3) * c

        return reward, done, win

    def step(self, action):
        row = action // SIZE
        col = action % SIZE
        if not self.board.is_empty((row, col)):
            return self.state, -30, False, {}

        self.board.put_stone((row, col), self.me)

        reward, done, win = self.calc_reward()
        reward_diff = reward - self.last_reward
        self.last_reward = reward
        info = {}

        if not done and self.board.has_empty_cell:
            rival_row, rival_col = self.rival.play(self.board).__next__()
            self.board.put_stone((rival_row, rival_col), self.rival)

            for x, y in self.board.utils.get_every_lines_indexes((rival_row, rival_col)):
                max_count, _ = self.rival.max_possibilities(self.board.map[x, y], self.rival, STONE_TURN - 1)
                if max_count >= WIN:
                    done = True

        if not self.board.has_empty_cell:
            done = True
            self.last_result = "Draw"
        elif done:
            if win:
                reward_diff += 100
                self.last_result = "Won"
            else:
                reward_diff -= 50
                self.last_result = "Lost"

        self.state = self.get_state()
        return self.state, reward_diff, done, info

    def reset(self, *, seed: Optional[int] = None, return_info: bool = False, options: Optional[dict] = None):
        if GUI:
            self.board = GUIBoard(size=SIZE)
            self.board.draw()
            self.board.show_message(self.last_result)
        else:
            self.board = Board(size=SIZE)

        rival_row, rival_col = self.rival.play(self.board).__next__()
        self.board.put_stone((rival_row, rival_col), self.rival)
        self.state = self.get_state()
        self.last_reward = 0
        return self.state


def build_model():
    input = Input((1, SIZE, SIZE, 2))

    layer0 = input
    conv1 = Conv2D(8, (2, 2), activation='relu')(layer0)
    conv2 = Conv2D(16, (2, 2), activation='relu')(conv1)
    conv3 = Conv2D(32, (2, 2), activation='relu')(conv2)

    part0 = Dense(256, activation='relu')(Flatten()(input))
    part1 = Dense(256, activation='relu')(Flatten()(conv1))
    part2 = Dense(256, activation='relu')(Flatten()(conv2))
    part3 = Dense(256, activation='relu')(Flatten()(conv3))

    fc1 = Concatenate()([part0, part1, part2, part3])
    fc2 = Dense(512, activation='relu', kernel_regularizer='L2')(fc1)
    fc3 = Dense(SIZE * SIZE, activation='linear')(fc2)

    outputs = fc3
    model = Model(inputs=input, outputs=outputs)
    model.summary()
    return model


if __name__ == '__main__':
    env = ConnectEnv()

    model = load_model('bots/ann.h5') if exists('bots/ann.h5') else build_model()
    policy = GreedyQPolicy()
    memory = SequentialMemory(limit=10000, window_length=1)
    dqn = DQNAgent(model=model, memory=memory, policy=policy,
                   nb_actions=SIZE * SIZE, nb_steps_warmup=10, target_model_update=1e-2)

    dqn.compile(Adam(lr=1e-3), metrics=['mse'])
    dqn.fit(env, nb_steps=500000, visualize=False, verbose=1)
    model.save('bots/ann.h5')
    print('Done')
