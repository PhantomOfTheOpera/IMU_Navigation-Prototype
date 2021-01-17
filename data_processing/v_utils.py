import numpy as np


def make_cube(coords, vectors, k=0.2):
    xx, xy, xz, yx, yy, yz, zx, zy, zz = vectors
    x, y, z = coords

    zx *= k
    zy *= k
    zz *= k

    dx = (xx + yx + zx) / 2 - x
    dy = (xy + yy + zy) / 2 - y
    dz = (xz + yz + zz) / 2 - z

    cube_definition = [(-dx, -dy, -dz), 
                (xx - dx, xy - dy, xz - dz), 
                (yx - dx, yy - dy, yz - dz), 
                (zx - dx, zy - dy, zz - dz)]

    cube_definition_array = [
        np.array(list(item))
        for item in cube_definition
    ]

    points = []
    points += cube_definition_array
    vectors = [
        cube_definition_array[1] - cube_definition_array[0],
        cube_definition_array[2] - cube_definition_array[0],
        cube_definition_array[3] - cube_definition_array[0]
    ]

    points += [cube_definition_array[0] + vectors[0] + vectors[1]]
    points += [cube_definition_array[0] + vectors[0] + vectors[2]]
    points += [cube_definition_array[0] + vectors[1] + vectors[2]]
    points += [cube_definition_array[0] + vectors[0] + vectors[1] + vectors[2]]

    points = np.array(points)

    edges = [
        [points[0], points[3], points[5], points[1]],
        [points[1], points[5], points[7], points[4]],
        [points[4], points[2], points[6], points[7]],
        [points[2], points[6], points[3], points[0]],
        [points[0], points[2], points[4], points[1]],
        [points[3], points[6], points[7], points[5]]
    ]

    return edges, points


def read_angular(path):
    lines = []
    with open(path) as f:
        for lin in f:
            lines.append(list(map(float, lin.split())))
    return lines