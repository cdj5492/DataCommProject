"""Entry point
"""

import matplotlib.pyplot as plt

from gui.gui import PlotGUI
from gui.netgrid_model import NetGridPresenter
from network.faces import Direction
from network.network_grid import NetworkGrid
from routing_algorithms.template import Template

UNIVERSE_DIMENSIONS = (8,8,8)


def init_simulator() -> NetworkGrid:
    # Main grid
    grid = NetworkGrid(Template())

    # Add some nodes to the grid
    grid.add_node(0, 0, 0)
    grid.add_node(1, 0, 0)
    grid.add_node(1, 1, 0)
    grid.add_node(2, 0, 0)
    
    # Initiate a packet transmission
    grid.get_node(2, 0, 0).send_packet(Direction.WEST, "Hello")

    return grid


def main():
    # Initialization
    simulator = init_simulator()
    model = NetGridPresenter(simulator)
    ui = PlotGUI(UNIVERSE_DIMENSIONS, model)
    model.add_observer(ui)

    # Display window
    plt.show()


if __name__ == "__main__":
    main()
