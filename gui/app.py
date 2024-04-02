"""Entry point
"""

import matplotlib.pyplot as plt

from gui import PlotGUI
from netgrid_model import NetGridPresenter
from network.network_grid import NetworkGrid

UNIVERSE_DIMENSIONS = (8,8,8)


def init_simulator() -> NetworkGrid:
    return NetworkGrid()


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
