import sys
import pygame
from tetris import Board
from pygame_handler import GraphicsHandler

def main():
    pygame.init()
    gh = GraphicsHandler()
    m_board = Board()

    gh.draw_main_menu()

    menuing = True

    while menuing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                menuing = False

    running = True

    clock = pygame.time.Clock()
    until_falling = 1000

    gravity = 1

    heldkeys = set()

    c_time = pygame.time.get_ticks()

    while running:
        o_time = c_time
        clock.tick()

        c_time = pygame.time.get_ticks()
        delta_t = c_time - o_time
        print(delta_t)
        sys.stdout.flush()

        # auto falling code
        until_falling -= gravity * delta_t
        if until_falling < 0:
            until_falling = 1000
            m_board.act('d')

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    m_board.act('l')
                elif event.key == pygame.K_RIGHT:
                    m_board.act('r')

                if event.key == pygame.K_UP:
                    m_board.act('cw')
                elif event.key == pygame.K_z:
                    m_board.act('ccw')

                if event.key == pygame.K_DOWN:
                    m_board.act('d')
                    until_falling = 1000
                elif event.key == pygame.K_SPACE:
                    m_board.act('hd')
                    until_falling = 1000
        
        gh.draw_game(m_board)
        pygame.display.update()

        if m_board.dead:
            running = False
    
    gh.draw_lose(m_board.score)
    pygame.display.update()

    waiting = True

    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menuing = False
    
    pygame.display.quit()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()