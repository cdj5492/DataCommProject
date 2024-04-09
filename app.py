"""Entry point

file: app.py
author: Mark Danza

Initializes and runs the network simulator and matplotlib GUI.
"""

import matplotlib.pyplot as plt

from gui.gui import PlotGUI
from gui.netgrid_model import NetGridPresenter
from network.faces import Direction
from network.network_grid import NetworkGrid
import routing_algorithms.template as routet
import robot_algorithm.template as robt


UNIVERSE_DIMENSIONS = (3,3,101)


def init_simulator() -> NetworkGrid:
    # Main grid
    grid = NetworkGrid(routet.Template(), robt.Template())

    # Add some nodes to the grid
    grid.add_node(0, 0, 0)
    grid.add_node(1, 0, 0)
    grid.add_node(1, 1, 0)
    grid.add_node(2, 0, 0)
    
    # add 100 in a line from 0,1,1 to 0,1,100
    for i in range(1, 101):
        grid.add_node(0, 1, i)
    
    grid.add_robot(0, 1, 0)
    
    # Initiate a packet transmission
    # grid.get_node(2, 0, 0).send_packet(Direction.WEST, "Hello")

    return grid


def main():
    # Initialization
    simulator = init_simulator()
    model = NetGridPresenter(simulator, UNIVERSE_DIMENSIONS)
    ui = PlotGUI(UNIVERSE_DIMENSIONS, model)
    model.add_observer(ui)
    plt.show()


if __name__ == "__main__":
    main()
