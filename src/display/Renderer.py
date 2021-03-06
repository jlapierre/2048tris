import pygame
from src.controls.InputProcessor import InputProcessor


class Renderer:
    background_color = 0x636363

    def __init__(self, board, square_size, padding_size, buffer_size):
        self.board = board
        self.square_size = square_size
        self.padding_size = padding_size
        self.buffer_size = buffer_size
        pygame.init()
        pygame.font.init()

        #TODO: make font surface, update and blit onto squares surface when drawing
        font = pygame.font.SysFont('Comic Sans MS', 30)

        surface_length = (square_size + padding_size) * (board.size + buffer_size * 2) + padding_size
        size = (surface_length, surface_length)
        self.surface = pygame.Surface(size)
        self.background = pygame.Rect(0, 0, surface_length, surface_length)
        self.screen = pygame.display.set_mode(size)
        self.clock = pygame.time.Clock()

    def render(self):
        running = True
        while running:
            event_list = pygame.event.get()
            self.update_board(event_list)
            self.draw_board()
            self.clock.tick(3)
            for event in event_list:
                if event.type == pygame.QUIT:
                    running = False
            if self.board.game_over:
                running = False

    def update_board(self, event_list):
        new_dir = InputProcessor.get_new_direction(event_list)
        piece_shift = InputProcessor.get_piece_shift(event_list)
        debug = InputProcessor.get_debug(event_list)
        if debug is not None:
            self.board.debug(debug)
        if new_dir is not None:
            self.board.change_direction(new_dir)
        if piece_shift is not None:
            if piece_shift == "drop":
                self.board.drop_active_piece()
            elif piece_shift == "rotate":
                self.board.rotate_active_piece()
            else:
                self.board.shift_active_piece(piece_shift)
        self.board.update_grid()

    def draw_board(self):
        self.get_board_image(self.board, self.square_size, self.padding_size, self.buffer_size, self.surface, self.background)
        self.screen.blit(self.surface, (0, 0))
        pygame.display.flip()

    @staticmethod
    def get_board_image(board, square_size, padding_size, buffer_size, surface, background):
        pygame.draw.rect(surface, pygame.Color(Renderer.background_color), background)
        for cell in board.grid.keys():
            if board.get_cell_value(cell) < 0:
                continue
            x = cell[0]
            y = cell[1]
            # x coordinate
            left = (square_size + padding_size) * x + padding_size + (buffer_size * square_size)
            # y coordinate
            top = (square_size + padding_size) * y + padding_size + (buffer_size * square_size)
            square = pygame.Rect(left, top, square_size, square_size)
            color = Renderer.get_color(board.get_cell_value(cell))
            pygame.draw.rect(surface, color, square)
            # todo: print value over square
        return surface

    @staticmethod
    def get_color(value):
        colors = {
            # gray
            0: 0xcccccc,
            # red
            2: 0xff0000,
            # orange
            4: 0xff8000,
            # yellow
            8: 0xffff00,
            # light green
            16: 0x00ff00,
            # dark green
            32: 0x009933,
            # aqua
            64: 0x00ffff,
            # blue
            128: 0x3399ff,
            # dark blue
            256: 0x0000ff,
            # purple
            512: 0x9933ff,
            # fuchsia
            1024: 0xff00ff,
            # black
            2048: 0x000000,
        }
        return colors.get(value, Renderer.background_color)
