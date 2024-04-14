"""Bellman-Ford Routing Algorithm

file: bellmanford.py
author: Mark Danza

Consumes a maximum of one packet from each node queue per simulation cycle and processes
or routes it according to the Bellman-Ford algorithm.
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
    Bellman-Ford Distance Table
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


class BellmanFordData:
    """
    Encapsulates a DistanceTbl with other state relevant for Bellman-Ford routing.

    This class should be used for RoutingCube.data.
    """

    def __init__(self, my_addr:node_addr_t):
        """
        Create new Bellman-Ford data with an empty distance table.

        :param my_addr: address of the node that owns this data
        """
        self.distance_tbl = DistanceTbl(my_addr) # BMF distance table
        self.last_dv = None # Last distance vector sent by this node
        self.tx_data = None # BMFDataPkt to send from this node


    def new_neighbor(self, addr:node_addr_t, link_cost:int):
        """
        Wrapper for DistanceTbl.new_neighbor().
        """
        return self.distance_tbl.new_neighbor(addr, link_cost)


    def update(self, distance_vector:dict[node_addr_t, int], via:node_addr_t):
        """
        Wrapper for DistanceTbl.update().
        """
        return self.distance_tbl.update(distance_vector, via)


    def next_hop(self, dest:node_addr_t) -> node_addr_t|None:
        """
        Wrapper for DistanceTbl.next_hop().
        """
        return self.distance_tbl.next_hop(dest)
    

    def get_distance_vector(self) -> dict[node_addr_t, int]:
        """
        Wrapper for DistanceTbl.get_distance_vector().
        """
        return self.distance_tbl.get_distance_vector()


class BellmanFordRouting(RoutingAlgorithm):
    """
    Routing algorithm class for Bellman-Ford.
    """
    
    def __init__(self):
        pass
    

    def got_new_neighbor_notif(self, cube:RoutingCube, neighbor_addr:node_addr_t, nn_pkt:BMFNewNeighborPkt):
        """
        Handles a new neighbor notification by updating the BMF distance table in the
        appropriate manner. If the given nn_pkt's ack attribute is not False, it will be
        set to False, and the packet will be sent back to the neighbor node, causing its
        distance table to be updated accordingly.

        :param cube: RoutingCube to operate on
        :param neighbor_addr: neighbor node address
        :param nn_pkt: neighbor notification packet
        """
        # Add neighbor to distance table
        cube.data.new_neighbor(neighbor_addr, nn_pkt.link_cost)
        if not nn_pkt.ack:
            # If this is not an Ack, acknowledge the neighbor by sending the packet back
            nn_pkt.ack = True
            cube.send_packet(determine_tx_dir(cube.position, neighbor_addr), nn_pkt)


    def send_new_neighbor_notif(self, cube:RoutingCube):
        """
        Generate and send a new neighbor notification packet in all directions at once.

        :param cube: RoutingCube to operate on
        """
        # Create new neighbor notification packet
        nn_pkt = BMFNewNeighborPkt()
        # Notify all neighbors
        for d in list(Direction):
            cube.send_packet(d, nn_pkt)


    def update_distance_tbl(self, cube:RoutingCube, neighbor_addr:node_addr_t, dv_pkt:BMFDistanceVectorPkt):
        """
        Update the cube's distance table with a distance vector from a neighbor node.

        :param cube: RoutingCube to operate on
        :param neighbor_addr: neighbor node address
        :param dv_pkt: distance vector packet from neighbor
        """
        cube.data.update(dv_pkt.vector, neighbor_addr)


    def update_neighbors(self, cube:RoutingCube):
        """
        Generate and send a distance vector packet in all directions at once. The new
        distance vector will only be sent if it is different from the last distance
        vector sent; otherwise, this method does nothing.

        :param cube: RoutingCube to operate on
        """
        # Create distance vector packet
        dv_pkt = BMFDistanceVectorPkt(cube.data.get_distance_vector())

        # Only update neighbors if distance table has not converged
        if cube.data.last_dv != dv_pkt.vector:
            for d in list(Direction):
                cube.send_packet(d, dv_pkt)
            cube.data.last_dv = dv_pkt.vector


    def route_pkt(self, cube:RoutingCube, pkt:BMFDataPkt):
        """
        Helper method for routing the given packet to the appropriate neighbor to reach
        its destination. If this cube is the packet's destination, this method does
        nothing.

        :param cube: RoutingCube to operate on
        :param pkt: data packet
        """
        # This cube is the destination
        if pkt.dest == cube.position:
            return
        
        # Route the packet toward the destination using Bellman Ford
        next_hop = cube.data.next_hop(pkt.dest)
        if next_hop is None:
            # This cube does not know a route to the destination
            cube.stats.num_pkts_dropped += 1
            return
        
        # Send the packet in the appropriate direction
        tx_dir = determine_tx_dir(cube.position, next_hop)
        cube.send_packet(tx_dir, pkt)


    def route(self, cube:RoutingCube):
        """
        Perform one cycle of Bellman-Ford routing.

        :param cube: RoutingCube to operate on
        :raises TypeError: if this cube receives a packet of an invalid type
        :return: cube
        """
        # Get a packet received by the cube
        pkt, rx_dir = cube.get_packet()
        if pkt is not None:
            # Determine the address of the packet sender based on the face it came from
            tx_addr = determine_tx_addr(cube.position, rx_dir)

            if isinstance(pkt, BMFNewNeighborPkt):
                # Cube got notified of new neighbor node - add the neighbor and send distance vector
                self.got_new_neighbor_notif(cube, tx_addr, pkt)
                self.update_neighbors(cube)
            
            elif isinstance(pkt, BMFDistanceVectorPkt):
                # Cube received distance vector from node - update table and send distance vector
                self.update_distance_tbl(cube, tx_addr, pkt)
                self.update_neighbors(cube)

            elif isinstance(pkt, BMFDataPkt):
                # Cube received data packet with a destination address
                self.route_pkt(cube, pkt)

            else:
                raise TypeError(f"Bad packet type: {type(pkt)}")
            
        # Transmit a packet generated by this cube if one exists
        if cube.data.tx_data is not None:
            self.route_pkt(cube, cube.data.tx_data)
            cube.data.tx_data = None
        
        return cube


    def power_on(self, cube:RoutingCube):
        """
        Initialize the cube's routing data and send new neighbor notifications to its
        neighbors.

        :param cube: RoutingCube to operate on
        """
        cube.data = BellmanFordData(cube.position)
        self.send_new_neighbor_notif(cube)

    
    def send_packet(self, cube:RoutingCube, dest_addr:node_addr_t, data:typing.Any):
        """
        Method used to trigger a packet transmission from this cube to the destination
        node, which will be handled by the routing algorithm.

        :param cube: RoutingCube to operate on
        :param data: packet payload
        :param dest_addr: destination node address
        """
        # Generate data packet with the destination address in this cube
        cube.data.tx_data = BMFDataPkt(dest_addr, data)


class BellmanFordRobot(RobotAlgorithm):
    """
    Bellman-Ford routing algorithm for robots. Simply treats the robot as a wrapper for
    a RoutingCube using the BellmanFordRouting algorithm.
    """

    CUBE_ROUTING_ALGO = BellmanFordRouting()

    def __init__(self):
        pass


    def step(self, robot: Robot) -> RoutingCube:
        BellmanFordRobot.CUBE_ROUTING_ALGO.route(robot.cube)
        

    def power_on(self, robot: Robot):
        BellmanFordRobot.CUBE_ROUTING_ALGO.power_on(robot.cube)
