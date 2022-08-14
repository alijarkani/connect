import time
import random
from board import Board


class Game(object):
    def __init__(self, board: Board,
                 players,
                 delay=.25,
                 shuffle_players=True,
                 win=6,
                 stone_each_turn=2):
        """Game handler"""
        self._board = board
        self._players = players
        self._active_player = 0
        self._turn_number = -1
        self._win = win
        self._stone_each_turn = stone_each_turn
        self._delay = delay

        if shuffle_players:
            random.shuffle(self._players)

        for player in self.players:
            player.prepare(self._board, self)

    @property
    def players(self):
        return self._players

    @property
    def active_player(self):
        return self._active_player

    @property
    def turn_number(self):
        return self._turn_number

    @property
    def win(self):
        return self._win

    @property
    def stone_each_turn(self):
        return self._stone_each_turn

    @property
    def player(self):
        return self._players[self._active_player]

    def turn(self):
        self._turn_number += 1
        self._active_player = self._turn_number % len(self._players)
        self._board.show_message(self.player.title + "'s Turn")
        return self.player

    def handle(self):
        self._board.draw()

        while self._board.has_empty_cell:
            player = self.turn()
            actions_count = 0
            for point in player.play(self._board):
                self._board.put_stone(point, player)

                if not self._board.has_empty_cell:
                    break

                if self._delay:
                    self._board.rest(self._delay)


                max_vicinity = self._board.get_max_partition(player, point)
                if max_vicinity and max_vicinity.count >= self._win:
                    self._board.show_winner(player, max_vicinity)
                    time.sleep(3)
                    return player

                actions_count += 1
                if actions_count >= self._stone_each_turn:
                    break

        self._board.show_draw()
        time.sleep(3)
