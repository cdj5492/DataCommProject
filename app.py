"""Entry point

file: app.py
author: Mark Danza

Initializes and runs the network simulator and matplotlib GUI.

Example execution:
$ python app.py bmf -n data/networks/net1.txt -r data/recipes/net1_1.txt -s 3 -c pkt-flow
"""

import argparse
import os
import sys

import matplotlib.pyplot as plt

from gui.color_conf import VALID_COLOR_CONFS
from gui.gui import PlotGUI
from gui.netgrid_model import NetGridPresenter
from network.network_grid import NetworkGrid
from network.sim.file import init_routingcubes_from_file
from network.sim.recipe import Recipe
from routing_algorithms.bellmanford import BellmanFordRouting, BellmanFordRobot
import routing_algorithms.template as routet
import robot_algorithm.template as robt


routing_algos = {
    "template" : (routet.Template, robt.Template),
    "bmf" : (BellmanFordRouting, BellmanFordRobot),
}


def _get_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "algorithm",
        default="template",
        type=str,
        choices=list(routing_algos.keys()),
        help="Routing algorithm to use."
    )
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
    parser.add_argument(
        "--size", "-s",
        default=10,
        type=int,
        required=False,
        help="Network size, which is used to determine the maximum coordinates displayed."
    )
    parser.add_argument(
        "--colormode", "-c",
        default="pkt-flow",
        type=str,
        choices=VALID_COLOR_CONFS,
        help="Display color mode to use."
    )
    return parser


def init_simulator(routing_algo_name:str, net_file_path:os.PathLike|None=None) -> NetworkGrid:
    """
    Initialize a NetworkGrid and populate it with the nodes specified in the given
    network file.

    :param routing_algo_name: string identifier of routing algorithm to use
    :param net_file_path: optional path to file containing network node information
    :return: network simulator object
    """
    # Instantiate routing and robot algorithm classes
    routing_alg_t, robo_alg_t = routing_algos[routing_algo_name]
    routing_alg, robo_alg = routing_alg_t(), robo_alg_t()

    # Main grid
    grid = NetworkGrid(routing_alg, robo_alg)

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
    simulator = init_simulator(cliargs.algorithm, cliargs.network)
    if cliargs.recipe is not None:
        recipe = Recipe.from_file(cliargs.recipe)
    else:
        recipe = None

    universe_dimensions = (cliargs.size, cliargs.size, cliargs.size)

    model = NetGridPresenter(simulator, universe_dimensions, recipe)
    ui = PlotGUI(model, universe_dimensions, cliargs.colormode)
    model.add_observer(ui)

    plt.show()


if __name__ == "__main__":
    main(sys.argv[1:])
