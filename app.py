"""Entry point

file: app.py
author: Mark Danza

Initializes and runs the network simulator and matplotlib GUI.

Example execution:
$ python app.py -n data/networks/net1.txt -r data/recipes/net1_1.txt
"""

import argparse
import os
import sys

import matplotlib.pyplot as plt

from gui.gui import PlotGUI
from gui.netgrid_model import NetGridPresenter
from network.network_grid import NetworkGrid
from network.sim.file import init_routingcubes_from_file
from network.sim.recipe import Recipe
import routing_algorithms.template as routet
import robot_algorithm.template as robt

UNIVERSE_DIMENSIONS = (3,3,3)


def _get_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--network", "--net", "-n",
        default=None,
        type=str,
        required=False,
        help="Specify network file containing initial node coordinates."
    )
    parser.add_argument(
        "--recipe", "-r",
        default=None,
        type=str,
        required=False,
        help="Specify recipe file containing simulation instructions."
    )
    return parser


def init_simulator(net_file_path:os.PathLike|None=None) -> NetworkGrid:
    """
    Initialize a NetworkGrid and populate it with the nodes specified in the given
    network file.

    :param net_file_path: optional path to file containing network node information
    :return: network simulator object
    """
    # TODO Workaround for bug in robot algorithm template
    robo_alg = robt.Template()
    robo_alg.step = lambda _ : None

    # Main grid
    grid = NetworkGrid(routet.Template(), robo_alg)

    if net_file_path is not None:
        # Add nodes to the grid
        cubes = init_routingcubes_from_file(net_file_path)
        for cube in cubes:
            x, y, z = cube.position
            grid.add_node(x, y, z, cube)

    return grid


def main(argv):
    # Parse CLI args
    parser = _get_argparser()
    cliargs = parser.parse_args(argv)

    # Initialization
    simulator = init_simulator(cliargs.network)
    if cliargs.recipe is not None:
        recipe = Recipe.from_file(cliargs.recipe)
    else:
        recipe = None

    model = NetGridPresenter(simulator, UNIVERSE_DIMENSIONS, recipe)
    ui = PlotGUI(UNIVERSE_DIMENSIONS, model)
    model.add_observer(ui)

    plt.show()


if __name__ == "__main__":
    main(sys.argv[1:])
