import copy
import random
from collections import deque
from datetime import datetime
import os
import sys

import numpy as np
import utils


class Piece:
    rotation_table = {'cw': 1, 'ccw': -1}

    # called with the piece_str e.g. 'S' representing which piece
    # can be I, J, L, O , S, T, Z pieces
    def __init__(self, piece_str, parent_game):
        """Tetromino class, used to represent a live piece

        Parameters
        ----------
        piece_str : str
            Letter used to name the piece (I, O, T, J, L, S, Z)
        parent_game : Board
            Parent game this piece belongs to, used to check if Piece is valid

        Attributes
        ----------
        piece_str : str
            Letter used to name the piece (I, O, T, J, L, S, Z)
        rotation : int
            Rotational value (0 pointing up, 1 to the right, etc)
        last_move : str
            Record of the last valid move the piece made
        """
        self.piece_str = piece_str
        self._parent_game = parent_game
        self.rotation = 0
        self.last_move = None

        # sets the spawning location (compensates for O's shape by moving it forward one column)
        self.pos = [6, 4 if piece_str == 'O' else 3]

    # rotates the piece (rotates the _shape matrix)
    def _rotate(self, direc):
        self.rotation = (self.rotation + direc) % 4
        if not self._parent_game._piece_valid():
            self.rotation = (self.rotation - direc) % 4
            return False
        return True

    # moves the piece in the desired direction
    # 'd', 'l', or 'r'
    def _move(self, direc: str) -> bool:
        index = 0 if direc in ('u', 'd') else 1
        amt = 1 if direc in ('d', 'r') else -1

        self.pos[index] += amt

        if not self._parent_game._piece_valid():
            self.pos[index] -= amt
            return False
        return True

    # returns the board indicies currently occupied by this piece
    def occupied(self):
        for spot in utils.OCCUPIED[self.piece_str][self.rotation]:
            yield tuple(map(sum, zip(self.pos, spot)))

    def act(self, action: str) -> bool:
        """Interface for Piece class - manipulates the piece as given

        Parameters
        ----------
        action : str
            Name of the action being performed - u, d, l, r, cw, or ccw

        Returns
        -------
        bool
            Whether or not the action succeeded
        """
        if action in utils.ROTATIONS:
            if self._rotate(self.rotation_table[action]):
                self.last_move = action
                return True
        elif action in utils.MOVEMENT:
            if self._move(action):
                self.last_move = action
                return True
        else:
            raise ValueError('Invalid move \'{}\''.format(action))

        return False


class Board:
    def __init__(self, board=None, rseed=None):
        """Main board class, built on top of numpy array

        Parameters
        ----------
        board : numpy.array, optional
            Board state, by default None which generates an empty board
        rseed : Any, optional
            Seed used by random.seed() for rng, by default None
        """

        self.height = 26
        self.playable_height = 20
        self.width = 10

        if board is None:
            self._board = np.array([[0 for i in range(self.width)]
                                    for i in range(self.height)])
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

    def _out_of_bounds(self, pos):
        if not 0 <= pos[0] < self.height or not 0 <= pos[1] < self.width:
            return True
        return False

    # checks if the current location of the piece is valid
    #   i.e. doesn't intersect with already placed blocks / out of bounds
    def _piece_valid(self):
        return not any(self._out_of_bounds(pos) or self._board[pos] != 0 for pos in self.cur_piece.occupied())

    # picks a random new piece
    #   modify this if want to switch to bag/other randomizer
    def _pick_new_next(self):
        self.next_pieces.extend(np.random.permutation(utils.SHAPES))

    # spawns a new piece in
    # also checks validity of spawned piece to see if game is lost
    def _spawn_piece(self):
        self._hold_used = False
        self.cur_piece = Piece(self.next_pieces.popleft(), self)
        if len(self.next_pieces) < 7:
            self._pick_new_next()
        self._generate_ghost_piece()

        if not self._piece_valid():
            self.dead = True

    def _hold(self):
        if self.held_piece is not None:
            self.next_pieces.appendleft(self.held_piece)
        self.held_piece = self.cur_piece.piece_str
        self._spawn_piece()
        self._hold_used = True

    def _generate_ghost_piece(self):
        og_piece = copy.deepcopy(self.cur_piece)
        while self.cur_piece.act('d'):
            pass

        self.ghost_piece_occupied = tuple(self.cur_piece.occupied())
        self.cur_piece = og_piece

    def _tspun(self):
        if self.cur_piece.piece_str != 'T' or self.cur_piece.last_move not in utils.ROTATIONS:
            return False

        corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
        filled_corners = 0

        #print('pos {}'.format(self.cur_piece.pos))

        for corner in corners:
            tocheck = tuple(map(sum, zip(corner, self.cur_piece.pos)))
            if self._out_of_bounds(tocheck) or self._board[tocheck] != 0:
                filled_corners += 1

        if filled_corners >= 3:
            return True
        return False

    # clears lines as needed and award points
    def _clear_lines(self, mult):

        lcleared = 0
        for r_ind in range(self.height):
            if all(val != 0 for val in self._board[r_ind]):
                for l_ind in reversed(range(1, r_ind + 1)):
                    self._board[l_ind] = self._board[l_ind - 1]
                self._board[0] = 0
                self.score += mult * 1000 * (lcleared + 1)
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

        mult = 2 if self._tspun() else 1
        # if mult == 2: print ("tspin")
        self._clear_lines(mult)
        self._spawn_piece()

    # valid actions: u, d, l, or r for movement
    # cw or ccw for rotation
    # returns   -1 for invalid action
    #           0 for failed action (e.g. piece became invalid)
    #           1 for successful action
    def act(self, action):
        if action == 'hold':
            if self._hold_used:
                return False
            self._hold()
        elif action == 'hd':
            while self.cur_piece.act('d'):
                pass
            self.lock_piece()
        elif action in utils.MOVEMENT:
            if not self.cur_piece.act(action):
                return False
        elif action in utils.ROTATIONS:
            offsets = utils.SRS_TABLE.get_rotation(
                self.cur_piece.piece_str, self.cur_piece.rotation, utils.ROTATION_TO_VAL[action])

            for offset in offsets:
                old_pos = self.cur_piece.pos
                self.cur_piece.pos = list(
                    utils.vector_add(self.cur_piece.pos, offset))

                if self.cur_piece.act(action):
                    break
                self.cur_piece.pos = old_pos
            else:
                return False
        else:
            raise ValueError('Invalid move \'{}\''.format(action))

        if action != 'd':
            self._generate_ghost_piece()

        return True

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
        print('Score: {}'.format(b.score))
        while True:
            print('Enter move (l, d, r, hd, cw, ccw, hold): ', end='')
            move = input()
            try:
                b.act(move)
                break
            except ValueError as e:
                print(e)

        if b.dead:
            break


if __name__ == "__main__":
    main()
