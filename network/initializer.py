"""Utility for NetworkGrid Initialization

file: initializer.py
author: Mark Danza

This contains a helper function for initializing a NetworkGrid with RoutingCubes from a
file.
"""

import os

from network.network_grid import NetworkGrid
from network.sim.file import init_routingcubes_from_file
from routing_algorithms.support import ROUTING_ALGOS


def init_simulator(routing_algo_name:str, net_file_path:os.PathLike|None=None) -> tuple[NetworkGrid, tuple[int,int,int]]:
    """
    Initialize a NetworkGrid and populate it with the nodes specified in the given
    network file.

    :param routing_algo_name: string identifier of routing algorithm to use
    :param net_file_path: optional path to file containing network node information
    :return: network simulator object, tuple of universe dimensions for plotting
    """
    max_x, max_y, max_z = 0, 0, 0

    # Instantiate routing and robot algorithm classes
    routing_alg_t, robo_alg_t = ROUTING_ALGOS[routing_algo_name]
    routing_alg, robo_alg = routing_alg_t(), robo_alg_t()

    # Main grid
    grid = NetworkGrid(routing_alg, robo_alg)

    if net_file_path is not None:
        # Add nodes to the grid
        cubes = init_routingcubes_from_file(net_file_path)
        for cube in cubes:
            x, y, z = cube.position
            grid.add_node(x, y, z, cube)

            # Track maximum cube coordinates
            if x > max_x:
                max_x = x
            if y > max_y:
                max_y = y
            if z > max_z:
                max_z = z

    return grid, (max_x+1, max_y+1, max_z+1)
