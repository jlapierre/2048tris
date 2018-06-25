from src.logic.PieceFactory import PieceFactory
from src.logic.TransformPiece import TransformPiece


class Board:
    def __init__(self, size):
        """Represents the grid, its cell values, and active piece"""
        self.size = size
        self.grid = {}
        self.init_grid(size)
        self.current_direction = "down"
        # if not empty, should be 4 tuples representing the coordinates of the moving piece
        self.active_piece = None
        self.game_over = False

    def init_grid(self, size):
        for x in range(size):
            for y in range(size):
                self.set_cell_value((x, y), 0)

    def update_grid(self):
        """shift active piece, handle any collisions"""
        if self.game_over:
            return
        if self.active_piece is None:
            self.place_new_piece()
        if self.piece_collision_exists(self.active_piece):
            self.handle_active_piece_collision()
            self.place_new_piece()
        self.shift_cells(self.active_piece, self.current_direction)
        self.active_piece = TransformPiece.shift_coordinates(self.active_piece, self.current_direction)
        self.merge_with_completed_rows()
        if self.is_game_won():
            self.game_over = True

    def get_max_cell_value(self):
        return max(list(self.grid.values()))

    def get_cell_value(self, coords):
        value = self.grid.get(coords)
        return value if value is not None else -1

    def set_cell_value(self, coords, value):
        self.grid[coords] = value

    def place_new_piece(self):
        """Place a new random piece at the start point and make that the active piece"""
        new_piece = PieceFactory.get_piece()
        new_piece = TransformPiece.transform(new_piece, PieceFactory.get_start_point(self.size, self.current_direction))
        self.active_piece = new_piece
        value = PieceFactory.get_value()
        for cell in self.active_piece:
            self.set_cell_value(cell, value)

    def active_piece_contains(self, coords):
        """Is the given coordinate pair part of the active piece"""
        return coords in self.active_piece

    def get_adjacent_value(self, coords, direction):
        """get the value of the adjacent cell. empty cell has a value of zero. nonexistent cell has a value of -1"""
        adjacent = TransformPiece.get_adjacent_coordinates(coords, direction)
        return self.get_cell_value(adjacent)

    def is_out_of_bounds(self, coords):
        x = coords[0]
        y = coords[1]
        return x < 0 or y < 0 or x >= self.size or y >= self.size

    def cell_collision_exists(self, coords, exempt_cells):
        adjacent_coords = TransformPiece.get_adjacent_coordinates(coords, self.current_direction)
        adjacent_value = self.get_cell_value(adjacent_coords)
        return adjacent_coords not in exempt_cells and \
               (adjacent_value > 0 or
                (adjacent_value == -1 and not self.is_in_buffer(adjacent_coords, self.current_direction)))

    def piece_collision_exists(self, cells):
        return any(self.cell_collision_exists(coords, cells) for coords in cells)

    def any_in_buffer(self, piece, direction):
        return any(self.is_in_buffer(cell, direction) for cell in piece)

    def is_in_buffer(self, coords, direction):
        if direction == "down":
            return coords[1] < 0
        elif direction == "up":
            return coords[1] >= self.size
        elif direction == "right":
            return coords[0] < 0
        elif direction == "left":
            return coords[0] >= self.size

    def change_direction(self, direction):
        if self.current_direction == direction or self.any_in_buffer(self.active_piece, self.current_direction):
            return
        self.current_direction = direction
        self.static_drop()
        self.place_new_piece()

    def drop_active_piece(self):
        self.active_piece = self.drop(self.active_piece)
        self.handle_active_piece_collision()

    def static_drop(self):
        """Drop all cells on the board as individuals, including the active piece"""
        if self.any_in_buffer(self.active_piece, self.current_direction):
            return
        for cell in TransformPiece.sort_cells(self.grid.keys(), self.current_direction):
            self.drop([cell])

    def shift_active_piece(self, direction):
        if self.current_direction == direction or TransformPiece.get_opposite_direction(self.current_direction) == direction:
            return
        self.shift_cells(self.active_piece, direction)
        self.active_piece = TransformPiece.shift_coordinates(self.active_piece, direction)

    def drop(self, cells):
        """drop the given cell(s) until at least one reaches a collision"""
        while not self.piece_collision_exists(cells):
            self.shift_cells(cells, self.current_direction)
            cells = TransformPiece.shift_coordinates(cells, self.current_direction)
        return cells

    def is_row_complete(self, row):
        """is the given row/column of cells complete"""
        return not any(self.get_cell_value(coords) == 0 for coords in row)

    def shift_column(self, coords, direction):
        """shifts the given column/row by one to fill the given empty cell"""
        self.shift_cells(self.get_column(coords, direction), direction)

    def get_column(self, coords, direction):
        """gets the remainder of the column/row above the given empty cell"""
        column = []
        x = coords[0]
        y = coords[1]
        if direction == "down":
            # x, 0-y
            for i in range(y):
                column.append((x, i))
        elif direction == "right":
            # 0-x, y
            for i in range(x):
                column.append((i, y))
        elif direction == "up":
            # x, y-last
            for i in range(y + 1, self.size):
                column.append((x, i))
        elif direction == "left":
            # x-last, y
            for i in range(x + 1, self.size):
                column.append((i, y))

        return column

    def get_column_inclusive(self, coords, direction):
        """returns the column up to and including the given cell"""
        column = self.get_column(coords, direction)
        column.append(coords)

        return column

    def do_static_merge(self, topCell, bottomCell):
        """merge the given matching cells and shift others accordingly"""
        self.set_cell_value(topCell, self.get_cell_value(topCell) * 2)
        self.shift_column(bottomCell, self.current_direction)
        self.drop_unattached()

    def merge_with_completed_rows(self):
        """check for completed rows and merge matching cells down into them"""
        if self.current_direction == "down":
            # each row starting at the bottom
            for i in reversed(range(self.size)):
                row = self.get_column_inclusive((0, i), "left")
                if self.is_row_complete(row):
                    for cell in row:
                        cell_above = TransformPiece.get_adjacent_coordinates(cell, "up")
                        self.do_static_merge(cell_above, cell)
        elif self.current_direction == "right":
            for i in reversed(range(self.size)):
                row = self.get_column_inclusive((0, i), "down")
                if self.is_row_complete(row):
                    for cell in row:
                        cell_above = TransformPiece.get_adjacent_coordinates(cell, "left")
                        self.do_static_merge(cell_above, cell)
        elif self.current_direction == "up":
            for i in range(self.size):
                row = self.get_column_inclusive((0, i), "left")
                if self.is_row_complete(row):
                    for cell in row:
                        cell_above = TransformPiece.get_adjacent_coordinates(cell, "down")
                        self.do_static_merge(cell_above, cell)
        elif self.current_direction == "left":
            for i in range(self.size):
                row = self.get_column_inclusive((0, i), "down")
                if self.is_row_complete(row):
                    for cell in row:
                        cell_above = TransformPiece.get_adjacent_coordinates(cell, "right")
                        self.do_static_merge(cell_above, cell)

    def drop_unattached(self):
        """find all pieces not attached to any others and drop them"""
        for x in range(self.size):
            for y in range(self.size):
                coords = (x, y)
                if self.is_cell_unattached(coords):
                    self.drop([coords])

    def is_cell_unattached(self, coords):
        return self.get_cell_value(coords) != 0 \
               and self.get_adjacent_value(coords, "up") < 1 \
               and self.get_adjacent_value(coords, "down") < 1 \
               and self.get_adjacent_value(coords, "left") < 1 \
               and self.get_adjacent_value(coords, "right") < 1

    def is_piece_unattached(self, piece):
        # todo: account for walls
        is_unattached = True
        # move_down = not any
        for cell in piece:
            if self.get_cell_value(cell) == 0:
                # ignore empty cells
                continue
            surrounding_cells = list(map(lambda direction: TransformPiece.get_adjacent_coordinates(cell, direction),
                                         ["up", "down", "left", "right"]))
            no_outside_adjacents = all(self.get_cell_value(xy) == 0 or xy in piece for xy in surrounding_cells)
            is_unattached = is_unattached and no_outside_adjacents
        return is_unattached

    def handle_active_piece_collision(self):
        for cell in self.active_piece:
            adjacent_cell = TransformPiece.get_adjacent_coordinates(cell, self.current_direction)
            adjacent_value = self.get_adjacent_value(cell, self.current_direction)
            if self.cell_collision_exists(cell, self.active_piece) and self.get_cell_value(cell) == adjacent_value:
                self.set_cell_value(adjacent_cell, adjacent_value * 2)
                self.clear_cell(cell)
        # move down remaining active cells if they are floating
        if self.is_piece_unattached(self.active_piece):
            self.shift_cells(self.active_piece, self.current_direction)

        # if piece is out of bounds, declare game over
        if any(self.is_out_of_bounds(cell) for cell in self.active_piece):
            self.game_over = True

    def shift_cells(self, cells, direction):
        """shift the given cells by one in the given direction, ignoring empty ones"""
        # sorted so cells within the same piece won't run into each other
        sorted_cells = TransformPiece.sort_cells(cells, direction)
        for cell in sorted_cells:
            value = self.get_cell_value(cell)
            if value < 1:
                continue
            adjacent_coords = TransformPiece.get_adjacent_coordinates(cell, direction)
            adjacent_value = self.get_cell_value(adjacent_coords)
            if adjacent_value < 1:
                # shift cell into empty space
                self.set_cell_value(adjacent_coords, value)
                self.clear_cell(cell)
            elif adjacent_value == value:
                # do merge
                self.set_cell_value(adjacent_coords, value * 2)
                self.clear_cell(cell)

    def clear_cell(self, cell):
        if self.is_out_of_bounds(cell):
            self.set_cell_value(cell, -1)
        else:
            self.set_cell_value(cell, 0)

    def is_game_won(self):
        return self.get_max_cell_value() >= 2048
