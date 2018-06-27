import random
import math

class PieceFactory:
    i = [(0, -1), (0, 0), (0, 1), (0, 2)]
    o = [(0, 0), (0, 1), (1, 0), (1, 1)]
    t = [(0, 0), (1, 0), (2, 0), (1, 1)]
    s = [(0, 1), (1, 0), (1, 1), (2, 0)]
    z = [(0, 0), (1, 0), (1, 1), (1, 2)]
    j = [(1, 0), (1, 1), (1, 2), (0, 2)]
    l = [(0, 0), (0, 1), (0, 2), (1, 2)]

    pieces = [i, o, t, s, z, j, l]

    @staticmethod
    def get_piece():
        """return a random tetris piece with relative coordinates"""
        return random.choice(PieceFactory.pieces)

    @staticmethod
    def get_value():
        """return 2 or 4 as the value of the cells in the new piece, with a 90% chance of a 2"""
        return random.choice([2, 2, 2, 2, 2, 2, 2, 2, 2, 4])

    @staticmethod
    def get_start_point(board_size, direction):
        if direction == "right":
            return -4, math.floor(board_size / 2)
        elif direction == "left":
            return board_size + 4, math.floor(board_size / 2)
        elif direction == "down":
            return math.floor(board_size / 2), -4
        elif direction == "up":
            return math.floor(board_size / 2), board_size + 4
