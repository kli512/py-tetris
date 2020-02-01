from copy import deepcopy

CLOCKWISE = 1
COUNTERCLOCKWISE = -1

ACTIONS = {
    'cw': 0,
    'ccw': 1,
    'u': 2,
    'd': 3,
    'l': 4,
    'r': 5,
    'd': 6,
    'hd': 7,
}

ROTATIONS = dict((key, val)
                 for key, val in ACTIONS.items() if key in ('cw', 'ccw'))

MOVEMENT = dict((key, val)
                for key, val in ACTIONS.items() if key in ('u', 'd', 'l', 'r'))

ROTATION_TO_VAL = {
    'cw': 1,
    'ccw': -1
}

def vector_add(v_1, v_2):
    for i in range(len(v_1)):
        yield v_1[i] + v_2[i]


SHAPES = ['T', 'S', 'Z', 'J', 'L', 'I', 'O']

_shape = {
    'T':
    [[0, 1, 0],
     [1, 1, 1],
     [0, 0, 0]],

    'S':
    [[0, 2, 2],
     [2, 2, 0],
     [0, 0, 0]],

    'Z':
    [[3, 3, 0],
     [0, 3, 3],
     [0, 0, 0]],

    'J':
    [[4, 0, 0],
     [4, 4, 4],
     [0, 0, 0]],

    'L':
    [[0, 0, 5],
     [5, 5, 5],
     [0, 0, 0]],

    'I':
    [[0, 0, 0, 0],
     [6, 6, 6, 6],
     [0, 0, 0, 0],
     [0, 0, 0, 0]],

    'O':
    [[7, 7],
     [7, 7]]
}


def _rotate(mat, times):
    output = deepcopy(mat)
    for _ in range(times):
        output = list(map(list, zip(*output[::-1])))
    return output


_occupied_shapes = dict((key, [_rotate(val, r)
                               for r in range(4)]) for key, val in _shape.items())

OCCUPIED = {}

for shape_name, shape in _occupied_shapes.items():
    OCCUPIED[shape_name] = [[] for rot in range(4)]
    for rot in range(4):
        for r_i, row in enumerate(shape[rot]):
            for c_i, val in enumerate(row):
                if val != 0:
                    OCCUPIED[shape_name][rot].append((r_i, c_i))


shape_values = {
    'T': 1,
    'S': 2,
    'Z': 3,
    'J': 4,
    'L': 5,
    'I': 6,
    'O': 7
}

VAL_TO_COLOR = {
    0: (0, 0, 0),
    1: (255, 0, 255),
    2: (0, 255, 0),
    3: (255, 0, 0),
    4: (0, 0, 255),
    5: (255, 165, 0),
    6: (137, 207, 240),
    7: (255, 255, 0),
}


class _SRSTable():
    def __init__(self):
        self._JLSTZ_table = (((0, 0), (+1, 0), (+1, +1), (0, -2), (+1, -2)),
                             ((0, 0), (-1, 0), (-1, +1), (0, -2), (-1, -2)),
                             ((0, 0), (+1, 0), (+1, -1), (0, +2), (+1, +2)),
                             ((0, 0), (+1, 0), (+1, -1), (0, +2), (+1, +2)),
                             ((0, 0), (-1, 0), (-1, +1), (0, -2), (-1, -2)),
                             ((0, 0), (+1, 0), (+1, +1), (0, -2), (+1, -2)),
                             ((0, 0), (-1, 0), (-1, -1), (0, +2), (-1, +2)),
                             ((0, 0), (-1, 0), (-1, -1), (0, +2), (-1, +2)))

        self._I_table = (((0, 0), (-1, 0), (+2, 0), (-1, +2), (+2, -1)),
                         ((0, 0), (-2, 0), (+1, 0), (-2, -1), (+1, +2)),
                         ((0, 0), (+2, 0), (-1, 0), (+2, +1), (-1, -2)),
                         ((0, 0), (-1, 0), (+2, 0), (-1, +2), (+2, -1)),
                         ((0, 0), (+1, 0), (-2, 0), (+1, -2), (-2, +1)),
                         ((0, 0), (+2, 0), (-1, 0), (+2, +1), (-1, -2)),
                         ((0, 0), (-2, 0), (+1, 0), (-2, -1), (+1, +2)),
                         ((0, 0), (+1, 0), (-2, 0), (+1, -2), (-2, +1)))

    def get_rotation(self, piece, starting, direc):
        table = None

        if piece in ('J', 'L', 'S', 'T', 'Z'):
            table = self._JLSTZ_table
        elif piece == 'I':
            table = self._I_table
        elif piece == 'O':
            return (0, 0)

        index = 2 * starting
        if direc == CLOCKWISE:
            index += 1

        for i in range(len(table[index])):
            offset = table[index][i]
            yield (-offset[1], offset[0])


SRS_TABLE = _SRSTable()
