import numpy as np
from numpy.random import randint, choice
import time
from collections import defaultdict
from player import Player

"""
TODO

implement 4 moves for double rolls

negative rewards for pieces being taken / left alone

"""


class Board():
    
    def __init__(self):
        board = np.zeros(26)
        board[1] = 2
        board[12] = 5
        board[17] = 3
        board[19] = 5
        board[6] = -5
        board[8] = -3
        board[13] = -5
        board[24] = -2
        self.board = board
        self.x = Player("x", self.board)
        self.y = Player("y", self.board)

    def update_board(self, new_state):
        if new_state != (): self.board = new_state
        self.draw_board()

    def draw_board(self):
        bottom_board = self.board[1:13]
        bottom_board = bottom_board[::-1]
        top_board = self.board[13:25]
        bb = ["|    |" if p == 0 else ("|x" + str(p) + "|" if p > 0 else
                     ("|y" + str(p * -1) + "|")) for p in bottom_board]
        tb = ["|    |" if p == 0 else ("|x" + str(p) + "|" if p > 0 else
                        ("|y" + str(p * -1) + "|")) for p in top_board]
        tbs, bbs = "", ""
        for p in bb:
            bbs += p
        for p in tb:
            tbs += p
        print()
        print(tbs)
        print()
        print(bbs)
        print()
        print("x bar:", self.board[0])
        print("y bar:", self.board[25])
