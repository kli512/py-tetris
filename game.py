import os
from tetris import Board

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
        print('Enter move (d, l, r, cw, ccw): ', end='')
        move = input()
        res = b.act(move)

        if b.dead:
            break
    
    print(b)
    print("Game over! Score: {}".format(b.score))


if __name__ == "__main__":
    main()