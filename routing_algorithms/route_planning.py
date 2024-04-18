"""Route Planning Routing Algorithm

file: route_planning.py
author: Cole Johnson

TODO: Description
"""

import dataclasses
import typing

from network.robot import Robot
from network.routing_cube import RoutingCube
from network.faces import Direction
from robot_algorithm.robot_algorithm import RobotAlgorithm
from routing_algorithms.helpers import node_addr_t, determine_tx_dir, determine_tx_addr
from routing_algorithms.routing_algorithm import RoutingAlgorithm

BMF_DEFAULT_LINK_COST = 1


@dataclasses.dataclass
class BMFNewNeighborPkt:
    """
    Special packet type used when a node is powered on to notify its neighbors of its
    existence.
    """
    link_cost : int = BMF_DEFAULT_LINK_COST
    ack : bool = False


@dataclasses.dataclass
class BMFDistanceVectorPkt:
    """
    Special packet type used to send distance vectors to a node's neighbors.
    """
    vector: dict[node_addr_t, int]


@dataclasses.dataclass
class BMFDataPkt:
    """
    Generic packet type with a destination address that may not be a neighbor node.
    """
    dest: node_addr_t
    payload: typing.Any


class DistanceTbl:
    """
    Generic Distance Table
    """
    
    def __init__(self, my_addr:node_addr_t):
        """
        Create a distance table for a specific node.

        :param my_addr: address of the node that owns this distance table
        """
        self.my_addr = my_addr
        self._distances = dict() # Internal distance table data


    def new_neighbor(self, addr:node_addr_t, link_cost:int):
        """
        Update the distance table with a neighbor node (i.e., distance to addr via itself
        is link_cost).

        :param addr: neighbor node address
        :param link_cost: distance from this node to neighbor node
        """
        # Create dict for the neighbor if it is new
        if addr not in self._distances:
            self._distances[addr] = dict()
        # Distance to new neighbor via new neighbor is equal to specified link cost
        self._distances[addr][addr] = link_cost


    def update(self, distance_vector:dict[node_addr_t, int], via:node_addr_t):
        """
        Update the distance table using a distance vector received from a neighbor node
        (i.e., distance to destination via neighbor is distance from neighbor to
        destination plus distance to neighbor).

        :param distance_vector: mapping of destination addresses to partial link costs
        :param via: neighbor node address (address of the node to which the distances in
                    distance_vector are related))
        """
        # If the neighbor not is not yet known, add it
        if via not in self._distances:
            self.new_neighbor(via, 1)

        # Iterate over destinations and corresponding distances thru the neighbor node
        for dest, distance in distance_vector.items():
            # Skip destination if it is myself
            if dest != self.my_addr:

                # Create dict for the destination if it is new
                if dest not in self._distances:
                    self._distances[dest] = dict()

                # Distance to destination thru neighbor = distance from neighbor to dest + link cost to neighbor
                link_cost_to_via = self._distances[via][via]
                self._distances[dest][via] = distance + link_cost_to_via

    
    def next_hop(self, dest:node_addr_t) -> node_addr_t|None:
        """
        Given a destination address, determine the address of the neighbor which will
        provide the lowest-cost path.

        :param dest: destination node address
        :return: neighbor node address, or address of this node if it is equal to dest,
        or None if this node is not aware of the given destination
        """
        if dest == self.my_addr:
            return self.my_addr
        
        neighbor = None
        neighbor_cost = 0

        # Determine the neighbor with the minimum link cost to the destination
        if dest in self._distances:
            dest_row = self._distances[dest]
            for via, cost in dest_row.items():
                if neighbor is None or cost < neighbor_cost:
                    neighbor, neighbor_cost = via, cost

        return neighbor
    

    def get_distance_vector(self) -> dict[node_addr_t, int]:
        """
        Generate a distance vector that can be used to update neighbor nodes' distance
        tables.

        :return: mapping of destination addresses to their distances from this node
        """
        dv = dict()
        for dest, via_row in self._distances.items():
            dv[dest] = min(via_row.values())
        return dv

class NetNodeData:
    """
    Encapsulates all data used by a node in the network.

    This class should be used for RoutingCube.data.
    """

    def __init__(self):
        pass
    
class RobotData:
    def __init__(self):
        pass


class NetNodeRouting(RoutingAlgorithm):
    def __init__(self):
        pass
    
    def route(self, cube:RoutingCube):
        pass


    def power_on(self, cube:RoutingCube):
        pass

    
    def send_packet(self, cube:RoutingCube, dest_addr:node_addr_t, data:typing.Any):
        pass


class RoutePlanningRobot(RobotAlgorithm):
    def __init__(self):
        pass


    def step(self, robot: Robot) -> RoutingCube:
        pass
        

    def power_on(self, robot: Robot):
        pass
