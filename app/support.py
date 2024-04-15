"""Module for Exporting Supported App Options

file: support.py
author: Mark Danza

To provide application support for a new routing algorithm, import the relevant classes
here and add an entry to the ROUTING_ALGOS dictionary with a unique name.

To provide application support for a new node color configuration, import the relevant
classes here and add an entry to the NODE_COLOR_CONFS dictionary with a unique name.
"""

from gui.color_conf import CONF_NUM_PKTS_RECEIVED, CONF_ANY_PKTS_DROPPED, CONF_PKT_FLOW
from routing_algorithms.bellmanford import BellmanFordRouting, BellmanFordRobot
import routing_algorithms.template as routet
import robot_algorithm.template as robt

ROUTING_ALGOS = {
    "template" : (routet.Template, robt.Template),
    "bmf" : (BellmanFordRouting, BellmanFordRobot),
}
"""All supported routing algorithms. Values are RoutingAlgorithm, RobotAlgorithm tuples."""

VALID_ROUTING_ALGOS = set(ROUTING_ALGOS.keys())
"""String names of valid routing algorithms."""


NODE_COLOR_CONFS = {
    "pkt-rx" : CONF_NUM_PKTS_RECEIVED,
    "pkt-drop" : CONF_ANY_PKTS_DROPPED,
    "pkt-flow" : CONF_PKT_FLOW,
}
"""All supported node color configurations."""

VALID_COLOR_CONFS = set(NODE_COLOR_CONFS.keys())
"""String names of valid color modes."""
