"""
"""

import numpy as np

from gui.utils import Model

from network.network_grid import NetworkGrid
from network.routing_cube import RoutingCube


class NetGridPresenter(Model):
    def __init__(self, netgrid:NetworkGrid, max_size:int=8):
        self.netgrid = netgrid
        self.max_size = max_size
        super().__init__()

    
    def get_nodes(self) -> np.ndarray[tuple[int,int,int]]:
        node_map = self.netgrid.node_map
        node_positions = np.array(list(node_map.keys()), dtype=int)

        nodes = np.zeros((self.max_size,self.max_size,self.max_size))
        for x, y, z in node_positions:
            nodes[x,y,z] = 1

        return nodes
    

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
