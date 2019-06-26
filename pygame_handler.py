import pygame
from tetris import Board
import utils


class GraphicsHandler:
    def __init__(self):
        pygame.display.set_caption('teetris')

        self.win_width = 800
        self.win_height = 700
        self.play_width = 300
        self.play_height = 600
        self.block_size = 30

        self.win = pygame.display.set_mode((self.win_width, self.win_height))

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
        pos = (self.top_left_x() + self.play_width / 2,
               self.top_left_y() + self.play_height / 2)

        self._draw_centered_text(text, pos, size, color, bold)

    def _draw_board(self, bstate):
        tlx, tly = self.top_left_x(), self.top_left_y()

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

    def _draw_next_box(self, piece_str):
        tlx, tly = self.top_left_x() + self.play_width + 50, self.top_left_y() + 50
        self._draw_piece_box(piece_str, tlx, tly)

    def _draw_hold_box(self, piece_str):
        if piece_str == None:
            return
        tlx, tly = self.top_left_x() - 150, self.top_left_y() + 50
        self._draw_piece_box(piece_str, tlx, tly)

    def _draw_score(self, score):
        self._draw_text('Score: {}'.format(
            score), (self.top_left_x(), self.top_left_y() + self.play_height))

    def _clear_board(self):
        self.win.fill((0, 0, 0))

    def _draw_grid(self):
        tlx, tly = self.top_left_x(), self.top_left_y()
        for i in range(20):
            pygame.draw.line(self.win, (50, 50, 50), (tlx, tly + i*30),
                             (tlx + self.play_width, tly + i * 30))  # horizontal lines
            for j in range(10):
                pygame.draw.line(self.win, (50, 50, 50), (tlx + j * 30, tly),
                                 (tlx + j * 30, tly + self.play_height))  # vertical lines

    def draw_game(self, board):
        self._clear_board()
        self._draw_board(board.state())
        self._draw_grid()
        self._draw_score(board.score)
        self._draw_next_box(board.nextPiece)
        self._draw_hold_box(board.held_piece)
        # implement more drawings for the game e.g. controls

    def draw_main_menu(self):
        self._clear_board()
        self._draw_text_middle('Press any key', bold=True)
        pygame.display.update()\


    def draw_lose(self, score):
        self._clear_board()
        self._draw_text_middle(
            'You Lost\nYour Score was {}'.format(score), bold=True)

    def top_left_x(self):
        return (self.win_width - self.play_width) / 2

    def top_left_y(self):
        return (self.win_height - self.play_height) / 2

# tester code follows


def main():
    pygame.init()
    gh = GraphicsHandler()

    b = Board()

    gh.draw_main_menu()
    run = True
    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                gh.draw_game(b)
                pygame.display.update()

    pygame.display.quit()
    pygame.quit()
    quit()


if __name__ == "__main__":
    main()
