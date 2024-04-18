"""App Initialization Functions

file: initialization.py
author: Mark Danza

This contains various functions used for initializing the application.

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

from app.support import ROUTING_ALGOS
from gui.netgrid_model import NetGridPresenter
from network.network_grid import NetworkGrid, RoutingCube
from network.recipe import Recipe


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


def init_recipe_from_file(f:os.PathLike, check_arg_count:bool=True) -> Recipe:
    """
    Wrapper for Recipe.from_file().

    :param f: recipe file (.txt)
    :param check_arg_count: whether to validate the number of arguments given for
                            each command
    :raises ValueError: if the recipe file is formatted improperly
    :return: recipe containing the instructions loaded from the file
    """
    return Recipe.from_file(f, check_arg_count)


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
    
    # print out all the nodes in the grid
    for cube in grid.get_all_nodes():
        print(cube)

    return grid, (max_x+1, max_y+1, max_z+1)


def init_presenter(
    routing_algo_name:str,
    net_file_path:os.PathLike|None=None,
    recipe_file_path:os.PathLike|None=None,
    universe_size:int|None=None
) -> NetGridPresenter:
    """
    Perform all the initialization of a NetGridPresenter.

    :param routing_algo_name: string identifier of routing algorithm to use
    :param net_file_path: optional path to network file
    :param recipe_file_path: optional path to recipe file
    :param universe_size: optional universe size to use if the automatically calculated
                          dimensions are smaller
    :return: network model
    """
    # Simulation backend initialization
    simulator, universe_dimensions = init_simulator(routing_algo_name, net_file_path)
    if recipe_file_path is not None:
        recipe = init_recipe_from_file(recipe_file_path)
    else:
        recipe = None

    # Override automatically determined dimensions with user-specified dimensions
    if universe_size is not None:
        if any([universe_size > d for d in universe_dimensions]):
            universe_dimensions = (universe_size, universe_size, universe_size)

    # Presenter initialization
    return NetGridPresenter(simulator, universe_dimensions, recipe)
