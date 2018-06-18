from src.display.Renderer import Renderer
from src.logic.Board import Board
import math

board_size = 16
square_size = 30
padding_size = math.floor(square_size * .10)
buffer_size = 4 # number of squares outside the main board
board = Board(board_size)
renderer = Renderer(board, square_size, padding_size, buffer_size)
renderer.render()

