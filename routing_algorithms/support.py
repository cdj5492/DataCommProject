"""Module for Exporting Supported Routing Algorithm Classes

file: support.py
author: Mark Danza

To provide application support for a new routing algorithm, import the relevant classes
here and add an entry to the ROUTING_ALGOS dictionary with a unique name.
"""

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
