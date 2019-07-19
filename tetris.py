import copy
import random
from collections import deque
from datetime import datetime
import os
import sys

import numpy as np
import utils

class Piece:
    # called with the piece_str e.g. 'S' representing which piece
    # can be I, J, L, O , S, T, Z pieces
    def __init__(self, piece_str, r=5):
        self.piece_str = piece_str
        self._shape = utils.LETTER_TO_SHAPE[piece_str]
        self.rotation = 0

        # sets the spawning location (compensates for O's small size by moving it forward on column)
        self.pos = [r, 3]
        if piece_str == 'O':
            self.pos[1] += 1

    # rotates the piece (rotates the _shape matrix)
    # utils.CLOCKWISE and utils.COUNTERCLOCKWISE define rotation
    def _rotate(self, direc):
        if direc not in (utils.CLOCKWISE, utils.COUNTERCLOCKWISE):
            return False

        self.rotation = (self.rotation + direc) % 4

        self._shape = list(map(list, zip(*self._shape[::-1])))
        if direc == utils.COUNTERCLOCKWISE:
            self._shape = list(map(list, zip(*self._shape[::-1])))
            self._shape = list(map(list, zip(*self._shape[::-1])))
        return True

    # moves the piece in the desired direction
    # 'd', 'l', or 'r'
    def _move(self, direc):
        if direc == 'u':
            self.pos[0] -= 1
        elif direc == 'd':
            self.pos[0] += 1
        elif direc == 'l':
            self.pos[1] -= 1
        elif direc == 'r':
            self.pos[1] += 1
        else:
            return False
        return True

    # returns the board indicies currently occupied by this piece
    def occupied(self):
        occ = []
        for r in range(len(self._shape)):
            for c in range(len(self._shape[0])):
                if self._shape[r][c] != 0:
                    occ.append((r + self.pos[0], c + self.pos[1]))
        return occ

    def act(self, action):
        if action in ('cw', 'ccw'):
            self._rotate(utils.ROTATION_TO_VAL[action])
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

        self.height = 26
        self.playable_height = 20
        self.width = 10

        if board is None:
            self._board = np.array([[0 for i in range(self.width)] for i in range(self.height)])
        else:
            self._board = np.array(board)

        if rseed is None:
            rseed = datetime.now()

        random.seed(rseed)

        self.lines_cleared = 0
        self.score = 0
        self.dead = False
        self.held_piece = None
        self._hold_used = False

        self.cur_piece = None
        self.next_pieces = deque()
        self._pick_new_next()
        self._spawn_piece()
        self.ghost_piece_occupied = None
        self._generate_ghost_piece()

    # checks if the current location of the piece is valid
    #   i.e. doesn't intersect with already placed blocks
    def _piece_valid(self):
        for pos in self.cur_piece.occupied():
            if pos[0] >= self.height or pos[1] not in range(self.width):
                return False
            if self._board[pos] != 0:
                return False
        return True

    # picks a random new piece
    #   modify this if want to switch to bag/other randomizer
    def _pick_new_next(self):
        self.next_pieces.extend(np.random.permutation(utils.SHAPES))

    # spawns a new piece in
    # also checks validity of spawned piece to see if game is lost
    def _spawn_piece(self, newpiece=None):
        self._hold_used = False
        if newpiece is None:
            self.cur_piece = Piece(self.next_pieces.popleft())
            if len(self.next_pieces) < 7:
                self._pick_new_next()
        else:
            self.cur_piece = Piece(newpiece)
        self._generate_ghost_piece()

        if not self._piece_valid():
            self.dead = True
            return False
        return True

    def _hold_piece(self):
        newpiece = self.held_piece
        self.held_piece = self.cur_piece.piece_str
        self._spawn_piece(newpiece=newpiece)
        self._hold_used = True

    def _generate_ghost_piece(self):
        og_piece = copy.deepcopy(self.cur_piece)
        while self._piece_valid():
            self.cur_piece.act('d')
        self.cur_piece.act('u')

        self.ghost_piece_occupied = self.cur_piece.occupied()
        self.cur_piece = og_piece

    # clears lines as needed and award points
    def _clear_lines(self):
        lcleared = 0
        for r_ind in range(self.height):
            if all(val != 0 for val in self._board[r_ind]):
                for l_ind in reversed(range(1, r_ind + 1)):
                    self._board[l_ind] = self._board[l_ind - 1]
                self._board[0] = 0
                self.score += 1000 * (lcleared + 1)
                lcleared += 1

        self.lines_cleared += lcleared
        return lcleared

    # public interface; this is how the player will interact

    # locks _cur_piece in place and spawns a new one
    def lock_piece(self):
        safe = False
        for pos in self.cur_piece.occupied():
            self._board[pos] = utils.shape_values[self.cur_piece.piece_str]
            if pos[0] >= self.height - self.playable_height:
                safe = True
        if not safe:
            self.dead = True
        self._clear_lines()
        self._spawn_piece()

    # valid actions: u, d, l, or r for movement
    # cw or ccw for rotation
    # returns   -1 for invalid action
    #           0 for failed action (e.g. piece became invalid)
    #           1 for successful action
    def act(self, action):
        if action not in ['d', 'l', 'r', 'hd', 'cw', 'ccw', 'hold']:
            return -1

        if action == 'hold':
            if self._hold_used:
                return 0
            self._hold_piece()
            return 1

        if action == 'hd':
            while self._piece_valid():
                self.cur_piece.act('d')
            self.cur_piece.act('u')
            self.lock_piece()
            return 1

        og_piece = copy.deepcopy(self.cur_piece)
        self.cur_piece.act(action)

        if not self._piece_valid():
            if action in ('cw', 'ccw'):
                rotations = utils.SRS_TABLE.get_rotation(og_piece.piece_str, og_piece.rotation, utils.ROTATION_TO_VAL[action])
                for srs in rotations:
                    old_pos = self.cur_piece.pos
                    self.cur_piece.pos = list(utils.vector_add(self.cur_piece.pos, srs))
                    if self._piece_valid():
                        self._generate_ghost_piece()
                        return 1
                    else:
                        self.cur_piece.pos = old_pos

            self.cur_piece = og_piece
            return 0

        if action != 'd':
            self._generate_ghost_piece()

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
