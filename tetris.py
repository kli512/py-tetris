import copy
import random
from datetime import datetime
import os

import numpy as np
import utils

class Piece:

    # called with the piece_str e.g. 'S' representing which piece
    # can be I, J, L, O , S, T, Z pieces
    def __init__(self, piece_str):
        self.piece_str = piece_str
        self._shape = utils.shapes[piece_str] # the rotation is implicit in _shape

        # sets the spawning location (compensates for O's small size by moving it forward on column)
        self._pos = [0, 3]
        if piece_str == 'O':
            self._pos[1] += 1

    # rotates the piece (rotates the _shape matrix)
    # -1 is ccw, 1 is cw
    def _rotate(self, direc):
        if direc != -1 and direc != 1:
            return False

        self._shape = list(map(list, zip(*self._shape[::-1])))
        if direc == -1:
            self._shape = list(map(list, zip(*self._shape[::-1])))
            self._shape = list(map(list, zip(*self._shape[::-1])))
        return True

    # moves the piece in the desired direction
    # 'd', 'l', or 'r'
    def _move(self, direc):
        if direc == 'u':
            self._pos[0] -= 1
        elif direc == 'd':
            self._pos[0] += 1
        elif direc == 'l':
            self._pos[1] -= 1
        elif direc == 'r':
            self._pos[1] += 1
        else:
            return False
        return True

    # returns the board indicies currently occupied by this piece
    def occupied(self):
        occ = []
        for r in range(len(self._shape)):
            for c in range(len(self._shape[0])):
                if self._shape[r][c] != 0:
                    occ.append((r + self._pos[0], c + self._pos[1]))
        return occ

    def act(self, action):
        if action == 'cw':
            self._rotate(1)
            return True
        elif action == 'ccw':
            self._rotate(-1)
            return True
        elif action == 'u' or action == 'd' or action == 'l' or action == 'r':
            self._move(action)
            return True
        return False

class Board:

    # sets the board state and seeds the random generator
    def __init__(self, board=None, rseed=None):
        # initializes the physical board with 0's, representing empty in all spaces
        # if a prefilled board state is desired, it can be given
        if board is None:
            self._board = np.array([[0 for i in range(10)] for i in range(20)])
        else:
            self._board = np.array(board)

        if rseed is None:
            rseed = datetime.now()

        random.seed(rseed)

        self.score = 0
        self.dead = False
        self.held_piece = None
        self._hold_used = False

        self.cur_piece = None
        self._pick_new_next()
        self._spawn_piece()

    # checks if the current location of the piece is valid
    #   i.e. doesn't intersect with already placed blocks
    def _piece_valid(self):
        for pos in self.cur_piece.occupied():
            if not (0 <= pos[0] <= 19 and 0 <= pos[1] <= 9):
                return False
            if self._board[pos] != 0:
                return False
        return True

    # picks a random new piece
    #   modify this if want to switch to bag/other randomizer
    def _pick_new_next(self):
        self.next_piece = random.choice(list(utils.shapes))

    # spawns a new piece in (called after _lock_piece or at beginning)
    # also checks validity of spawned piece to see if game is lost
    def _spawn_piece(self, newpiece=None):
        self._hold_used = False
        if newpiece is None:
            self.cur_piece = Piece(self.next_piece)
            self._pick_new_next()
        else:
            self.cur_piece = Piece(newpiece)

        if not self._piece_valid():
            self.dead = True
            return False
        return True

    # clears lines as needed and award points
    def _clear_lines(self):
        lcleared = 0
        for r_ind in range(len(self._board)):
            if all(val != 0 for val in self._board[r_ind]):
                for l_ind in reversed(range(1, r_ind + 1)):
                    self._board[l_ind] = self._board[l_ind - 1]
                self._board[0] = 0
                self.score += 1000 * (lcleared + 1)
                lcleared += 1

        return lcleared

    # locks _cur_piece in place and spawns a new one
    def _lock_piece(self):
        for pos in self.cur_piece.occupied():
            self._board[pos] = utils.shape_values[self.cur_piece.piece_str]
        self._clear_lines()

    def _hold_piece(self):
        newpiece = self.held_piece
        self.held_piece = self.cur_piece.piece_str
        self._spawn_piece(newpiece=newpiece)
        self._hold_used = True

    # public interface; this is how the player will interact
    # action currently should be a string representing what the player
    # chose to do

    # valid actions: u, d, l, or r for movement
    # cw or ccw for rotation
    def act(self, action):
        if action not in ['d', 'l', 'r', 'hd', 'cw', 'ccw', 'hold']:
            return -1

        if action == 'hold':
            if self._hold_used:
                return 0
            self._hold_piece()
            return 1

        og_piece = None
        if action == 'hd':
            while self._piece_valid():
                self.cur_piece.act('d')
            self.cur_piece.act('u')
            og_piece = copy.deepcopy(self.cur_piece)
            self.cur_piece.act('d')
        else:
            og_piece = copy.deepcopy(self.cur_piece)
            self.cur_piece.act(action)

        if not self._piece_valid():
            self.cur_piece = og_piece
            if action == 'd' or action == 'hd':
                self._lock_piece()
                self._spawn_piece()
            else:
                return 0
        return 1

    def state(self):
        bstate = copy.deepcopy(self._board)
        for pos in self.cur_piece.occupied():
            bstate[pos] = utils.shape_values[self.cur_piece.piece_str]

        return bstate

    def __str__(self):
        temp = copy.deepcopy(self._board)
        for pos in self.cur_piece.occupied():
            temp[pos] = utils.shape_values[self.cur_piece.piece_str]

        out = np.array_str(temp)
        out = out.replace('0', ' ')

        return out

# testing to check functionality of board

def clear():
    os.system('cls||clear')

def main():
    b = Board()

    res = None
    move = None
    while True:
        print(b)
        if res == -1:
            print("Invalid action sequence '{}'".format(move))
        elif res == 0:
            print("Invalid piece movement '{}'".format(move))

        print('Score: {}'.format(b.score))
        print('Enter move (l, d, r, hd, cw, ccw): ', end='')
        move = input()
        res = b.act(move)

        if b.dead:
            break

if __name__ == "__main__":
    main()
