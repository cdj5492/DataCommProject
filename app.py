"""Entry point

file: app.py
author: Mark Danza

Initializes and runs the network simulator and matplotlib GUI.
"""

import os

import matplotlib.pyplot as plt

from gui.gui import PlotGUI
from gui.netgrid_model import NetGridPresenter
from network.network_grid import NetworkGrid
from network.sim.file import init_routingcubes_from_file
from network.sim.recipe import Recipe
import routing_algorithms.template as routet
import robot_algorithm.template as robt


UNIVERSE_DIMENSIONS = (3,3,3)
NET_FILE = r"data\networks\net1.txt"
RECIPE_FILE = r"data\recipes\net1_1.txt"


def init_simulator(net_file_path:os.PathLike|None=None) -> NetworkGrid:
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


def main():
    # Initialization
    simulator = init_simulator(NET_FILE)
    recipe = Recipe.from_file(RECIPE_FILE)

    model = NetGridPresenter(simulator, UNIVERSE_DIMENSIONS, recipe)
    ui = PlotGUI(UNIVERSE_DIMENSIONS, model)
    model.add_observer(ui)

    plt.show()


if __name__ == "__main__":
    main()
