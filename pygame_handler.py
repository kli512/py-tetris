import sys
import pygame
from tetris import Board
import utils


class GameHandler:
    def __init__(self, board):
        pygame.display.set_caption('Teetris')

        self.m_board = board

        self.key_map = {
            pygame.K_LEFT: 'l',
            pygame.K_RIGHT: 'r',
            pygame.K_UP: 'cw',
            pygame.K_z: 'ccw',
            pygame.K_DOWN: 'd',
            pygame.K_SPACE: 'hd',
            pygame.K_LSHIFT: 'hold'
        }

        self.win_width = 800
        self.win_height = 700
        self.play_width = 300
        self.play_height = 600
        self.block_size = 30

        self.win = pygame.display.set_mode((self.win_width, self.win_height))

    def _top_left_x(self):
        return (self.win_width - self.play_width) / 2

    def _top_left_y(self):
        return (self.win_height - self.play_height) / 2

    def _draw_text(self, text, pos, size=40, color=(255, 255, 255), bold=False):
        font = pygame.font.SysFont('arial', size, bold=bold)
        label = font.render(text, 1, color)

        self.win.blit(label, pos)

    def _draw_centered_text(self, text, pos, size=40, color=(255, 255, 255), bold=False):
        font = pygame.font.SysFont('arial', size, bold=bold)
        label = font.render(text, 1, color)
        textpos = (pos[0] - label.get_width() / 2,
                   pos[1] - label.get_height() / 2)

        self.win.blit(label, textpos)

    def _draw_text_middle(self, text, size=40, color=(255, 255, 255), bold=False):
        pos = (self._top_left_x() + self.play_width / 2,
               self._top_left_y() + self.play_height / 2)

        self._draw_centered_text(text, pos, size, color, bold)

    def _draw_board(self):
        tlx, tly = self._top_left_x(), self._top_left_y()

        bstate = self.m_board.state()

        for i in range(len(bstate)):
            for j in range(len(bstate[0])):
                pygame.draw.rect(self.win, utils.VAL_TO_COLOR[bstate[i][j]], (
                    tlx + j * self.block_size, tly + i * self.block_size, self.block_size, self.block_size), 0)

        pygame.draw.rect(self.win, (169, 169, 169), (tlx, tly,
                                                     self.play_width, self.play_height), 5)

    def _draw_piece_box(self, piece_str, tlx, tly):
        shape = utils.shapes[piece_str]
        color = utils.VAL_TO_COLOR[utils.shape_values[piece_str]]

        for i in range(len(shape)):
            for j in range(len(shape)):
                if shape[i][j] != 0:
                    pygame.draw.rect(self.win, color, (tlx + j * self.block_size,
                                                       tly + i * self.block_size, self.block_size, self.block_size), 0)

    def _draw_next_box(self):
        tlx, tly = self._top_left_x() + self.play_width + 50, self._top_left_y() + 50
        self._draw_piece_box(self.m_board.nextPiece, tlx, tly)

    def _draw_hold_box(self):
        held = self.m_board.held_piece
        if held is None:
            return
        tlx, tly = self._top_left_x() - 150, self._top_left_y() + 50
        self._draw_piece_box(held, tlx, tly)

    def _draw_score(self):
        self._draw_text('Score: {}'.format(
            self.m_board.score), (self._top_left_x(), self._top_left_y() + self.play_height))

    def _clear_board(self):
        self.win.fill((0, 0, 0))

    def _draw_grid(self):
        tlx, tly = self._top_left_x(), self._top_left_y()
        for i in range(20):
            pygame.draw.line(self.win, (50, 50, 50), (tlx, tly + i*30),
                             (tlx + self.play_width, tly + i * 30))  # horizontal lines
            for j in range(10):
                pygame.draw.line(self.win, (50, 50, 50), (tlx + j * 30, tly),
                                 (tlx + j * 30, tly + self.play_height))  # vertical lines

    def _draw_game(self):
        self._clear_board()
        self._draw_board()
        self._draw_grid()
        self._draw_score()
        self._draw_next_box()
        self._draw_hold_box()
        # implement more drawings for the game e.g. controls

    def _draw_main_menu(self):
        self._clear_board()
        self._draw_text_middle('Press any key', bold=True)
        pygame.display.update()

    def _draw_lose(self):
        self._clear_board()
        self._draw_text_middle(
            'You Lost\nYour Score was {}'.format(self.m_board.score), bold=True)

    def _menu_loop(self):
        self._draw_main_menu()
        menuing = True

        while menuing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    menuing = False

    def _game_loop(self):
        running = True

        clock = pygame.time.Clock()
        until_falling = 1000

        gravity = 1

        c_time = pygame.time.get_ticks()

        while running:
            o_time = c_time
            clock.tick()

            c_time = pygame.time.get_ticks()
            delta_t = c_time - o_time

            # auto falling code
            until_falling -= gravity * delta_t
            if until_falling < 0:
                until_falling = 1000
                self.m_board.act('d')

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    self.m_board.act(self.key_map[event.key])

            self._draw_game()
            pygame.display.update()

            if self.m_board.dead:
                running = False
    
    def _end_loop(self):
        self._draw_lose()
        pygame.display.update()

        waiting = True

        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False
        
        pygame.display.quit()
        pygame.quit()
        sys.exit()

    def play_game(self):
        pygame.init()
        self._menu_loop()
        self._game_loop()
        self._end_loop()