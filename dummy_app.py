"""Entry Point for GUI Test Using Dummy

file: dummy_app.py
author: Mark Danza
"""

import matplotlib.pyplot as plt

from dummy.dummy_model import DummyNetSimulator, UNIVERSE_DIMENSIONS
from gui.gui import PlotGUI


def main():
    # Initialization
    model = DummyNetSimulator()
    ui = PlotGUI(UNIVERSE_DIMENSIONS, model)
    model.add_observer(ui)

    # Display window
    plt.show()


if __name__ == "__main__":
    main()
