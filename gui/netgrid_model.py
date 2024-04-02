"""
"""

import numpy as np

from model import Model

from network.network_grid import NetworkGrid
from network.routing_cube import RoutingCube


class NetGridPresenter(Model):
    def __init__(self, netgrid:NetworkGrid):
        self.netgrid = netgrid
        super().__init__()

    
    def get_nodes(self) -> np.ndarray[tuple[int,int,int]]:
        node_map = self.netgrid.node_map
        return np.array(node_map.keys())
    

    def next_state(self):
        pass


    def prev_state(self):
        pass


    def restart(self):
        pass
