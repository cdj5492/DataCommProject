"""
"""

import numpy as np

from gui.utils import Model

from network.faces import Direction
from network.network_grid import NetworkGrid
from network.routing_cube import RoutingCube

HEX_RED = "red"
HEX_BLUE = "blue"


def _node_has_packet(node:RoutingCube):
    # TODO this should probably be a method of RoutingCube
    return any(
        node.faces.peek_packet(i) is not None
        for i in list(Direction)
    )


class NetGridPresenter(Model):
    def __init__(self, netgrid:NetworkGrid, dimensions:tuple[int,int,int]):
        self.netgrid = netgrid
        self.dimensions = dimensions
        super().__init__()

    
    def get_node_positions(self) -> np.ndarray[int]:
        node_map = self.netgrid.node_map
        node_positions = np.array(list(node_map.keys()), dtype=int)

        nodes = np.zeros(self.dimensions, dtype=int)
        for x, y, z in node_positions:
            nodes[x,y,z] = 1

        return nodes
    

    def get_node_facecolors(self) -> np.ndarray[str]:
        node_map = self.netgrid.node_map
        node_facecolors = np.zeros(self.dimensions, dtype=str)
        node_facecolors[:,:,:] = HEX_BLUE

        for (x,y,z), node in node_map.items():
            if _node_has_packet(node):
                node_facecolors[x,y,z] = HEX_RED                

        return node_facecolors


    def next_state(self):
        # Step the grid
        self.netgrid.step()
        self.alert_observers()


    def prev_state(self):
        # TODO Currently no way to access previous state
        self.alert_observers()


    def restart(self):
        # TODO Currently no way to reset to initial state
        pass
