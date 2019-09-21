from collections import defaultdict
import sys
from time import strftime
import pygame
from tetris import Board
import utils


class GameHandler:
    def __init__(self):
        pygame.display.set_caption('Teetris')

        self._modes = ['40L Sprint', 'Ultra']

        self.m_board = None

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

    # generic functions

    def quit_game(self):
        pygame.display.quit()
        pygame.quit()
        sys.exit()

    def _top_left_x(self):
        return (self.win_width - self.play_width) / 2

    def _top_left_y(self):
        return (self.win_height - self.play_height) / 2

    def _clear_board(self):
        self.win.fill((0, 0, 0))

    def _draw_text(self, text, pos, align=(-1, -1), size=40, color=(255, 255, 255), bold=False):
        font = pygame.font.SysFont('arial', size, bold=bold)
        label = font.render(text, 1, color)

        textpos = list(pos)
        if align[0] == 0:
            textpos[0] -= label.get_width() / 2
        elif align[0] == 1:
            textpos[0] -= label.get_width()

        if align[1] == 0:
            textpos[1] -= label.get_height() / 2
        elif align[1] == 1:
            textpos[1] -= label.get_height()

        self.win.blit(label, textpos)

    # menuing functions

    def _draw_selector(self, pos, size):
        points = (pos, (pos[0], pos[1] + size),
                  (pos[0] + size * (2 ** 0.5), pos[1] + size / 2))
        pygame.draw.polygon(self.win, (255, 255, 255), points)

    def _draw_main_menu(self, options, selected):
        self._clear_board()

        pos = [15, 10]
        self._draw_text('Modes', pos, size=30, bold=True)
        pos[0] += 50
        pos[1] += 50
        for o_i, option in enumerate(options):
            self._draw_text(' - ' + option, pos, size=20)
            if o_i == selected:
                self._draw_selector((pos[0] - 40, pos[1]), size=20)

            pos[1] += 30

        self._draw_text('Teetris', (self.win_width - 15,
                                    self.win_height - 10), align=(1, 1), bold=True)
        self._draw_text('Press any key', (self.win_width / 2,
                                          self.win_height / 2), (0, 0), bold=True)
        pygame.display.update()

    def _menu_loop(self):
        options = ['40L Sprint', 'Ultra', 'Exit']
        selected = 0
        menuing = True

        while menuing:
            self._draw_main_menu(options, selected)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()

                og_selection = selected
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected += 1
                    elif event.key == pygame.K_UP:
                        selected -= 1
                    elif event.key == pygame.K_RETURN:
                        return selected

                if selected not in range(len(options)):
                    selected = og_selection

    # gameplay functions

    def _draw_board(self):
        tlx, tly = self._top_left_x(), self._top_left_y()

        bstate = self.m_board.state()[(
            self.m_board.height - self.m_board.playable_height)::]

        for i in range(len(bstate)):
            for j in range(len(bstate[0])):
                pygame.draw.rect(self.win, utils.VAL_TO_COLOR[bstate[i][j]], (
                    tlx + j * self.block_size, tly + i * self.block_size, self.block_size, self.block_size))

        for pos in self.m_board.ghost_piece_occupied:
            if pos[0] >= self.m_board.height - self.m_board.playable_height:
                s = pygame.Surface((self.block_size, self.block_size))
                s.set_alpha(128)
                s.fill(
                    utils.VAL_TO_COLOR[utils.shape_values[self.m_board.cur_piece.piece_str]])
                self.win.blit(s, (tlx + pos[1] * self.block_size,
                                  tly + (pos[0] - 6) * self.block_size))

        pygame.draw.rect(self.win, (169, 169, 169), (tlx, tly,
                                                     self.play_width, self.play_height), 5)

    def _draw_piece_box(self, piece_str, tlx, tly):
        shape = utils.LETTER_TO_SHAPE[piece_str]
        color = utils.VAL_TO_COLOR[utils.shape_values[piece_str]]

        for i in range(len(shape)):
            for j in range(len(shape)):
                if shape[i][j] != 0:
                    pygame.draw.rect(self.win, color, (tlx + j * self.block_size,
                                                       tly + i * self.block_size, self.block_size, self.block_size))

    def _draw_next_boxs(self):
        tlx, tly = self._top_left_x() + self.play_width + 50, self._top_left_y() + 50
        for i in range(5):
            self._draw_piece_box(
                self.m_board.next_pieces[i], tlx, tly + i * self.block_size * 3)

    def _draw_hold_box(self):
        held = self.m_board.held_piece
        if held is None:
            return
        tlx, tly = self._top_left_x() - 150, self._top_left_y() + 50
        self._draw_piece_box(held, tlx, tly)

    def _draw_lines_cleared(self):
        self._draw_text('Lines: {}'.format(self.m_board.lines_cleared),
                        (self._top_left_x() + self.play_width/2, self._top_left_y()), (0, 1))

    def _draw_score(self):
        self._draw_text('Score: {}'.format(
            self.m_board.score), (self._top_left_x(), self._top_left_y() + self.play_height))

    def _draw_time(self):
        time = (pygame.time.get_ticks() - self.start_time) / 1000
        self._draw_text('Time: {:.2f}'.format(time),
                        (self._top_left_x() - 200, self._top_left_y() + self.play_height - 80), size=30)

    def _draw_grid(self):
        tlx, tly = self._top_left_x(), self._top_left_y()
        for i in range(self.m_board.playable_height):
            pygame.draw.line(self.win, (50, 50, 50), (tlx, tly + i*30),
                             (tlx + self.play_width, tly + i * 30))  # horizontal lines
            for j in range(self.m_board.width):
                pygame.draw.line(self.win, (50, 50, 50), (tlx + j * 30, tly),
                                 (tlx + j * 30, tly + self.play_height))  # vertical lines

    def _draw_game(self):
        self._clear_board()
        self._draw_board()
        self._draw_grid()
        self._draw_score()
        self._draw_time()
        self._draw_lines_cleared()
        self._draw_next_boxs()
        self._draw_hold_box()
        # implement more drawings for the game e.g. controls

    def _get_das_keys(self):
        keys = []
        for key, command in self.key_map.items():
            if command == 'l' or command == 'r':
                keys.append(key)
        return keys

    def _sprint_finished(self):
        if self.m_board.lines_cleared >= 40:
            return True
        return False

    def _ultra_finished(self):
        if pygame.time.get_ticks() - self.start_time > 120 * 1000:
            return True
        return False

    def _game_loop(self, mode):

        finished = None
        if mode == 0:
            finished = self._sprint_finished
        elif mode == 1:
            finished = self._ultra_finished
        else:
            finished = lambda: False

        self.m_board = Board()

        running = True

        clock = pygame.time.Clock()

        gravity = 1

        das = 100
        arr = 1
        soft_drop_rate = 1

        held_time = defaultdict(lambda: 0)
        arr_charge = defaultdict(lambda: 0)

        das_keys = self._get_das_keys()

        c_time = pygame.time.get_ticks()

        self.start_time = c_time

        until_falling = 1000
        lock_delay = 500

        while running:
            if finished():
                return True

            o_time = c_time
            clock.tick()

            c_time = pygame.time.get_ticks()
            delta_t = c_time - o_time

            # auto falling code
            until_falling -= gravity * delta_t
            if until_falling <= 0:
                if self.m_board.act('d') == 0:
                    if lock_delay <= 0:
                        self.m_board.lock_piece()
                        until_falling = 1000

                    lock_delay -= delta_t
                else:
                    # lock_delay = 500 # SEGA rotation lock delay
                    until_falling = 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()

                if event.type == pygame.KEYDOWN:
                    try:
                        if self.m_board.act(self.key_map[event.key]) == 1:
                            if self.key_map[event.key] == 'hold':
                                until_falling = 1000
                            lock_delay = 500  # Infinity lock delay
                    except KeyError:
                        continue  # skips this key event

                    if event.key in das_keys:
                        for key in das_keys:
                            held_time[key] = -delta_t
                            arr_charge[key] = -delta_t
                    elif event.key == pygame.K_DOWN:
                        arr_charge[event.key] = -delta_t

            keys = pygame.key.get_pressed()

            for key in das_keys:
                if keys[key]:
                    held_time[key] += delta_t

                    if held_time[key] > das:
                        arr_charge[key] += delta_t
                        while arr_charge[key] > arr:
                            arr_charge[key] -= arr
                            self.m_board.act(self.key_map[key])

            # should use a member variable/function that is the inverse mapping of key_map
            if keys[pygame.K_DOWN]:
                arr_charge[pygame.K_DOWN] += delta_t
                while arr_charge[pygame.K_DOWN] > soft_drop_rate:
                    arr_charge[pygame.K_DOWN] -= soft_drop_rate
                    self.m_board.act('d')

            self._draw_game()
            pygame.display.update()

            if self.m_board.dead:
                return False

    # postgame functions

    def _draw_lose(self):
        self._clear_board()
        self._draw_text('Your Score was {}'.format(self.m_board.score),
                        (self.win_width / 2, self.win_height / 2), (0, 0), bold=True)

    def _end_loop(self, mode, survived):
        # self._draw_lose()
        self._draw_text('Finished', (self.win_width,
                                     self.win_height), align=(1, 1), bold=True)
        pygame.display.update()

        waiting = True

        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False

        self.quit_game()

    def play_game(self):
        pygame.init()
        mode = self._menu_loop()
        if mode == 2:
            self.quit_game()
        survived = self._game_loop(mode)
        self._end_loop(mode, survived)
