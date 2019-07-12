import pygame
from tetris import Board
from pygame_handler import GameHandler

def main():
    pygame.init()
    gh = GameHandler(Board())

    gh.play_game()

if __name__ == "__main__":
    main()