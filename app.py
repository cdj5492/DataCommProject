"""Entry point

file: app.py
author: Mark Danza

Initializes and runs the network simulator and matplotlib GUI.

Example execution:
$ python app.py bmf -n data/networks/net1.txt -r data/recipes/net1_1.txt -c pkt-flow
"""

import argparse
import sys

import matplotlib.pyplot as plt

from app.initialization import init_presenter
from app.support import VALID_ROUTING_ALGOS, VALID_COLOR_CONFS
from gui.gui import PlotGUI


def _get_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "algorithm",
        default="template",
        type=str,
        choices=VALID_ROUTING_ALGOS,
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
        default=0,
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


def main(argv):
    # Parse CLI args
    parser = _get_argparser()
    cliargs = parser.parse_args(argv)

    # GUI frontend initialization
    model = init_presenter(cliargs.algorithm, cliargs.network, cliargs.recipe, cliargs.size)
    ui = PlotGUI(model, cliargs.colormode, cliargs.algorithm, cliargs.network, cliargs.recipe)
    model.add_observer(ui)

    # Give control to matplotlib
    plt.show()


if __name__ == "__main__":
    main(sys.argv[1:])
