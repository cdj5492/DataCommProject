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
from network.routing_cube import RoutingCube

COLOR_RED = "red"
COLOR_BLUE = "blue"


def _node_has_packet(node:RoutingCube):
    """
    Checks whether the given node contains a packet at any of its faces.

    :param node: routing cube
    :return: True if there is a packet in node
    """
    # TODO this should probably be a method of RoutingCube
    return any(
        node.faces.peek_packet(i) is not None
        for i in list(Direction)
    )


class NetGridPresenter(Model):
    """
    "Presenter" class that acts as an intermediary between the NetworkGrid backend and
    the user interface.
    """

    def __init__(self, netgrid:NetworkGrid, dimensions:tuple[int,int,int]):
        """
        Creates a presenter for the given grid.

        :param netgrid: simulator backend
        :param dimensions: (x,y,z) dimensions of grid to plot the network in
        """
        self.netgrid = netgrid
        self.dimensions = dimensions
        super().__init__()

    
    def get_node_positions(self) -> np.ndarray[int]:
        node_map = self.netgrid.node_map
        nodes = np.zeros(self.dimensions, dtype=int)
        
        for x, y, z in node_map.keys():
            nodes[x,y,z] = 1

        return nodes
    

    def get_node_facecolors(self) -> np.ndarray[str]:
        """
        Nodes containing packets are colored red. All other nodes are blue.
        """
        node_map = self.netgrid.node_map
        node_facecolors = np.zeros(self.dimensions, dtype=str)
        node_facecolors[:,:,:] = COLOR_BLUE

        for (x,y,z), node in node_map.items():
            if _node_has_packet(node):
                node_facecolors[x,y,z] = COLOR_RED                

        return node_facecolors


    def next_state(self):
        """
        Step the internal NetworkGrid.
        """
        self.netgrid.step()
        self.alert_observers()


    def prev_state(self):
        # TODO Currently no way to access previous state
        pass


    def restart(self):
        # TODO Currently no way to reset to initial state
        pass

    def skip_to_end(self):
        pass
