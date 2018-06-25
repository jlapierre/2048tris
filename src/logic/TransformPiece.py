class TransformPiece:

    @staticmethod
    def transform(piece, start_point):
        """transform the given piece in relative coordinates to the absolute coordinates"""
        new_piece = []
        for coord in piece:
            new_piece.append((coord[0] + start_point[0], coord[1] + start_point[1]))
        return new_piece

    @staticmethod
    def shift_coordinates(piece, direction):
        """shifts the given piece by 1 in the given direction (one of: 'up' 'down' 'left' 'right')"""
        if direction == 'up':
            return TransformPiece.transform(piece, (0, -1))
        elif direction == 'down':
            return TransformPiece.transform(piece, (0, 1))
        elif direction == 'left':
            return TransformPiece.transform(piece, (-1, 0))
        elif direction == 'right':
            return TransformPiece.transform(piece, (1, 0))
        else:
            # no valid direction given
            return piece

    @staticmethod
    def get_adjacent_coordinates(coords, direction):
        """returns the next coordinate pair in the given direction"""
        return TransformPiece.shift_coordinates([coords], direction)[0]

    @staticmethod
    def sort_cells(cells, direction):
        """return a sorted copy of the given cells with the 'bottom' cells first relative to the given direction"""
        lam = None
        if direction == "left" or direction == "right":
            lam = lambda cell: cell[0]
        elif direction == "up" or direction == "down":
            lam = lambda cell: cell[1]
        sorted_cells = list(sorted(cells, key=lam))
        if direction == "down" or direction == "right":
            sorted_cells.reverse()
        return sorted_cells

    @staticmethod
    def get_opposite_direction(direction):
        if direction == 'up':
            return "down"
        elif direction == 'down':
            return "up"
        elif direction == 'left':
            return "right"
        elif direction == 'right':
            return "left"
        else:
            # no valid direction given
            return None
