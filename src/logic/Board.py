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
                (adjacent_value == -1 and not self.is_in_buffer(adjacent_coords)))

    def piece_collision_exists(self, cells):
        return any(self.cell_collision_exists(coords, cells) for coords in cells)

    def any_in_buffer(self, piece):
        return any(self.is_in_buffer(cell) for cell in piece)

    def is_in_buffer(self, coords):
        """is the given cell in the buffer"""
        # technically should add conditions to not let the piece be off to the side of the buffer
        # however, given the board size the piece couldn't possibly get there in time so it's a non-issue
        direction = self.current_direction
        if direction == "down":
            return coords[1] < 0
        elif direction == "up":
            return coords[1] >= self.size
        elif direction == "right":
            return coords[0] < 0
        elif direction == "left":
            return coords[0] >= self.size

    def change_direction(self, direction):
        if self.current_direction == direction or self.any_in_buffer(self.active_piece):
            return
        self.current_direction = direction
        self.static_drop()
        self.place_new_piece()

    def drop_active_piece(self):
        self.active_piece = self.drop(self.active_piece)
        self.handle_active_piece_collision()

    def rotate_active_piece(self):
        if TransformPiece.is_square(self.active_piece):
            return
        transformed_active_piece = TransformPiece.rotate(self.active_piece)
        # do not allow rotation if it would cause an invalid (non-combo) overlap
        for c in range(len(transformed_active_piece)):
            cell = transformed_active_piece[c]
            if cell in self.active_piece:
                continue
            space_val = self.get_cell_value(cell)
            if space_val != 0 and space_val != self.get_cell_value(self.active_piece[c]):
                return
        # value of each cell in the active piece
        val = self.get_cell_value(self.active_piece[0])
        collision = False
        for cell in self.active_piece:
            self.clear_cell(cell)
        self.active_piece = transformed_active_piece
        for c in range(len(transformed_active_piece)):
            new_cell = transformed_active_piece[c]
            space_val = self.get_cell_value(new_cell)
            if space_val == val:
                self.set_cell_value(new_cell, val * 2)
                collision = True
            else:
                self.set_cell_value(new_cell, val)
        # if piece is out of bounds after a collision, declare game over
        if collision and any(self.is_out_of_bounds(cell) for cell in self.active_piece):
            self.game_over = True


    def static_drop(self):
        """Drop all cells on the board as individuals, including the active piece"""
        if self.any_in_buffer(self.active_piece):
            return
        for cell in TransformPiece.sort_cells(self.grid.keys(), self.current_direction):
            self.drop([cell])

    def shift_active_piece(self, direction):
        if self.current_direction == direction:
            return
        elif TransformPiece.get_opposite_direction(self.current_direction) == direction:
            self.rotate_active_piece()
            return
        new_coords = TransformPiece.shift_coordinates(self.active_piece, direction)
        for cell in new_coords:
            if self.is_out_of_bounds(cell) and not self.is_in_buffer(cell):
                return
        merged = self.shift_cells(self.active_piece, direction)
        self.active_piece = new_coords
        if merged:
            self.active_piece = None

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
        # sort so the given cell isn't just tacked on the end
        if direction == "up" or direction == "down":
            # sort by y
            column.sort(key=lambda c: c[1])
        elif direction == "left" or direction == "right":
            # sort by x
            column.sort(key=lambda c: c[0])

        return column

    def do_static_merge(self, top_cell, bottom_cell):
        """if their values match, merge the given cells and shift others accordingly"""
        if self.get_cell_value(top_cell) != self.get_cell_value(bottom_cell):
            return
        self.set_cell_value(top_cell, self.get_cell_value(top_cell) * 2)
        self.clear_cell(bottom_cell)
        self.shift_column(bottom_cell, self.current_direction)
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
        is_unattached = True
        for cell in piece:
            if self.get_cell_value(cell) <= 0:
                # ignore empty cells
                continue
            surrounding_cells = list(map(lambda direction: TransformPiece.get_adjacent_coordinates(cell, direction),
                                         ["up", "down", "left", "right"]))
            no_outside_adjacents = all(self.get_cell_value(xy) <= 0 or xy in piece for xy in surrounding_cells)
            is_unattached = is_unattached and no_outside_adjacents
        return is_unattached

    def handle_active_piece_collision(self):
        cells_to_merge = []
        for cell in self.active_piece:
            adjacent_cell = TransformPiece.get_adjacent_coordinates(cell, self.current_direction)
            if adjacent_cell in self.active_piece:
                continue
            adjacent_value = self.get_adjacent_value(cell, self.current_direction)
            if self.get_cell_value(cell) == adjacent_value:
                cells_to_merge.append(cell)
            elif adjacent_value != 0:
                # the whole piece cannot shift down without breaking, so do not merge
                return
        for cell in TransformPiece.sort_cells(self.active_piece, self.current_direction):
            if cell in cells_to_merge:
                # do merge
                self.set_cell_value(TransformPiece.get_adjacent_coordinates(cell, self.current_direction), self.get_cell_value(cell) * 2)
            else:
                # shift down
                self.set_cell_value(TransformPiece.get_adjacent_coordinates(cell, self.current_direction), self.get_cell_value(cell))
            self.clear_cell(cell)

        # if piece is out of bounds, declare game over
        if any(self.is_out_of_bounds(cell) for cell in self.active_piece):
            self.game_over = True

    def shift_cells(self, cells, direction):
        """shift the given cells by one in the given direction, returns whether a merge occurred"""
        merge = False
        # sorted so cells within the same piece won't run into each other
        sorted_cells = TransformPiece.sort_cells(cells, direction)
        # if trying to shift past a wall, abort mission
        for cell in sorted_cells:
            value = self.get_cell_value(cell)
            if value < 1:
                continue
            adjacent_coords = TransformPiece.get_adjacent_coordinates(cell, direction)
            adjacent_value = self.get_cell_value(adjacent_coords)
            if adjacent_value == -1 and not self.is_in_buffer(adjacent_coords):
                return
        # do shift
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
                merge = True
        return merge

    def clear_cell(self, cell):
        if self.is_out_of_bounds(cell):
            self.set_cell_value(cell, -1)
        else:
            self.set_cell_value(cell, 0)

    def is_game_won(self):
        return self.get_max_cell_value() >= 2048

    def debug(self, command):
        if command == "print_grid":
            # print the current grid as a visualized array
            Board.visualize(self.grid, self.size)

    @staticmethod
    def visualize(grid, board_size=16):
        """prints the given grid as a visualized 2D array of values"""
        visual_grid = []
        for i in range(board_size):
            row = []
            for j in range(board_size):
                row.append(grid[(j, i)])
            visual_grid.append(row)
        print(visual_grid)
