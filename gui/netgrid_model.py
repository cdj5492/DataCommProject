"""Model Class for NetworkGrid Simulator

file: netgrid_model.py
author: Mark Danza

This contains a class which encapsulates a NetworkGrid object with the functions required
for any network simulator Model.
"""

import numpy as np

from gui.utils import Model

from network.faces import Direction
from network.network_grid import NetworkGrid
from network.robot import Robot
from network.routing_cube import RoutingCube
from network.sim.recipe import Recipe

COLOR_RED = "red"
COLOR_BLUE = "blue"
COLOR_GREEN = "green"


def _node_has_packet(node:RoutingCube):
    """
    Checks whether the given node contains a packet at any of its faces.

    :param node: routing cube
    :return: True if there is a packet in node
    """
    # TODO this should probably be a method of RoutingCube
    return any(
        node.faces.peek_packet(d) is not None
        for d in list(Direction)
    )


def _node_is_robot(node:RoutingCube, robots:list[Robot]) -> bool:
    # TODO this should probably be a method of NetworkGrid
    return any([bot.cube.position == node.position for bot in robots])


class NetGridPresenter(Model):
    """
    "Presenter" class that acts as an intermediary between the NetworkGrid backend and
    the user interface.
    """

    def __init__(self, netgrid:NetworkGrid, dimensions:tuple[int,int,int], recipe:Recipe|None=None):
        """
        Creates a presenter for the given grid.

        :param netgrid: simulator backend
        :param dimensions: (x,y,z) dimensions of grid to plot the network in
        """
        self.netgrid = netgrid
        self.dimensions = dimensions
        self.recipe = recipe
        super().__init__()

    
    def get_node_positions(self) -> np.ndarray[int]:
        node_map = self.netgrid.node_map
        nodes = np.zeros(self.dimensions, dtype=int)
        
        for x, y, z in node_map.keys():
            nodes[x,y,z] = 1

        return nodes
    

    def get_node_facecolors(self) -> np.ndarray[str]:
        """
        Nodes containing packets are colored red. Nodes representing robot connection
        points are colored green. All other nodes are blue.
        """
        node_map = self.netgrid.node_map
        node_facecolors = np.zeros(self.dimensions, dtype=str)

        for (x,y,z), node in node_map.items():
            if _node_has_packet(node):
                node_facecolors[x,y,z] = COLOR_RED
            elif _node_is_robot(node, self.netgrid.robot_list):
                node_facecolors[x,y,z] = COLOR_GREEN
            else:
                node_facecolors[x,y,z] = COLOR_BLUE 

        return node_facecolors


    def next_state(self):
        """
        Step the internal NetworkGrid and recipe, if applicable. If a recipe exists, it
        is stepped first.
        """
        # Execute next recipe cycle
        if self.recipe is not None:
            # Resume recipe if paused
            self.recipe.resume()
            self.recipe.execute_next(self.netgrid)
        # Step network grid and update observers
        self.netgrid.step()
        self.alert_observers()


    def prev_state(self):
        # TODO Currently no way to access previous state
        pass


    def restart(self):
        # TODO Currently no way to reset to initial state
        pass


    def run(self):
        """
        Repeatedly steps to the next state until the internal recipe is finished running.
        Does nothing if there is no recipe.

        WARNING: This function will block forever if the recipe has an infinite loop.
        """
        # TODO Add more sophisticated diagnostics
        if self.recipe is not None:
            # Resume recipe if paused
            self.recipe.resume()
            # Execute recipe cycles and step network grid until paused
            while self.recipe.is_running():
                self.recipe.execute_next(self.netgrid)
                self.netgrid.step()
            # Update observers with resulting state
            self.alert_observers()
