"""Functions for Working with Network Initialization Files

file: files.py
author: Mark Danza

Network File Formatting:
 - One node per line.
 - Each line contains the x,y,z coordinates of a normal node, space-delimited.
 - Robot nodes cannot be specified in network files. To add robot nodes to a network, use
   a recipe.
 - Blank lines and commented lines (starting with '#') are ignored.
"""

import os
import typing

import numpy as np

from network.network_grid import RoutingCube


def init_routingcubes_from_file(f:os.PathLike) -> list[RoutingCube]:
    """
    Initialize a list of routing cubes from the given file.

    :param f: network file (.txt)
    :raises ValueError: if the network file is formatted improperly
    :return: list of RoutingCube objects with positions loaded from the file
    """
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
    """
    Write the positions of the given routing cubes to a text file.

    :param f: path to save network file (.txt)
    :param cubes: collection of routing cubes
    """
    nodes = np.ndarray((len(cubes), 3), dtype=int)

    for i, cube in enumerate(cubes):
        nodes[i] = cube.position

    np.savetxt(f, nodes, delimiter=' ', header="Leave comments with '#'", comments='#')
