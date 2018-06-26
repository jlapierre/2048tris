import numpy


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

    @staticmethod
    def rotate(piece):
        """rotate piece counter-clockwise"""
        new_piece = []
        # declare rotation vector
        rotation_vector = [[0, -1], [1, 0]]
        # get pivot point: avg x, avg
        x = numpy.round(numpy.mean(list(map(lambda c: c[0], piece))), 0)
        y = numpy.round(numpy.mean(list(map(lambda c: c[1], piece))), 0)
        pivot = (int(x), int(y))
        for cell in piece:
            if cell != pivot:
                # get relative coords to pivot
                relative_cell = [(cell[0] - pivot[0]), (cell[1] - pivot[1])]
                # matrix multiply to get relative transformed cell
                relative_transformed = numpy.dot(rotation_vector, relative_cell)
                # add back in distance to pivot to get abs coord
                abs_transformed = (int(relative_transformed[0] + pivot[0]), int(relative_transformed[1] + pivot[1]))
                # append abs transformed cell to new_piece
                new_piece.append(abs_transformed)
            else:
                new_piece.append((int(cell[0]), int(cell[1])))
        return new_piece

    @staticmethod
    def is_square(piece):
        """are the given coordinates a square?"""
        # [cell_0] [cell_1]
        # [cell_2] [cell_3]
        # ^ checking for the other 3 cells relative to 0
        min_x = min(piece, key=lambda c: c[0])[0]
        cell_0 = min(filter(lambda cl: cl[0] == min_x, piece), key=lambda c: c[1])
        cell_1 = False
        cell_2 = False
        cell_3 = False
        for cell in piece:
            if cell == cell_0:
                continue
            elif cell[0] == cell_0[0] + 1 and cell[1] == cell_0[1]:
                cell_1 = True
            elif cell[0] == cell_0[0] and cell[1] == cell_0[1] + 1:
                cell_2 = True
            elif cell[0] == cell_0[0] + 1 and cell[1] == cell_0[1] + 1:
                cell_3 = True
        return cell_1 and cell_2 and cell_3

