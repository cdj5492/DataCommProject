"""
file: files.py
author: Mark Danza
"""

import os
import typing

import numpy as np

from network.network_grid import RoutingCube


def init_routingcubes_from_file(f:os.PathLike) -> list[RoutingCube]:
    nodes = np.loadtxt(f, dtype=int, comments='#', delimiter=' ')
    cubes = list()

    for row in nodes:
        # Each row must contain x,y,z coordinates of a node
        if len(row) != 3:
            raise ValueError("Invalid input file for network grid")
        
        x, y, z = row
        cube = RoutingCube((x, y, z))
        cubes.append(cube)

    return cubes


def save_routingcubes_to_file(f:os.PathLike, cubes:typing.Iterable[RoutingCube]):
    nodes = np.ndarray((len(cubes), 3), dtype=int)

    for i, cube in enumerate(cubes):
        nodes[i] = cube.position

    np.savetxt(f, nodes, delimiter=' ', header="Leave comments with '#'", comments='#')
