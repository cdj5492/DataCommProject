import dataclasses
from typing import Dict, Optional
import typing

from network.robot import Robot
from network.routing_cube import RoutingCube
from network.faces import Direction
from robot_algorithm.robot_algorithm import RobotAlgorithm
from routing_algorithms.helpers import node_addr_t, determine_tx_dir, determine_tx_addr
from routing_algorithms.routing_algorithm import RoutingAlgorithm


BMF_DEFAULT_LINK_COST = 1
@dataclasses.dataclass
class NewNeighborPkt:
    """
    Special packet type used when a node is powered on to notify its neighbors of its
    existence.
    """
    link_cost : int = BMF_DEFAULT_LINK_COST
    ack : bool = False


@dataclasses.dataclass
class DistanceVectorPkt:
    """
    Special packet type used to send distance vectors to a node's neighbors.
    """
    vector: dict[node_addr_t, int]


@dataclasses.dataclass
class DataPkt:
    """
    Generic packet type with a destination address that may not be a neighbor node.
    """
    dest: node_addr_t
    payload: typing.Any




@dataclasses.dataclass
class DijkstraDistanceTbl:
    """
    Dijkstra Distance Table
    """

    def __init__(self, my_addr: node_addr_t):
        """
        Create a distance table for a specific node.

        :param my_addr: address of the node that owns this distance table
        """
        self.my_addr = my_addr
        self._distances: Dict[node_addr_t, int] = {}
        self._visited: Dict[node_addr_t, bool] = {}

    def new_neighbor(self, addr: node_addr_t, link_cost: int):
        """
        Update the distance table with a neighbor node (i.e., distance to addr via itself
        is link_cost).

        :param addr: neighbor node address
        :param link_cost: distance from this node to neighbor node
        """
        self._distances[addr] = link_cost
        self._visited[addr] = False

    def update(self, distance_vector: Dict[node_addr_t, int], via: node_addr_t):
        """
        Update the distance table using a distance vector received from a neighbor node
        (i.e., distance to destination via neighbor is distance from neighbor to
        destination plus distance to neighbor).

        :param distance_vector: mapping of destination addresses to partial link costs
        :param via: neighbor node address (address of the node to which the distances in
                    distance_vector are related)
        """
        for dest, distance in distance_vector.items():
            if dest != self.my_addr:
                new_distance = distance + self._distances.get(via, float("inf"))
                if new_distance < self._distances.get(dest, float("inf")):
                    self._distances[dest] = new_distance

    def next_hop(self) -> Optional[node_addr_t]:
        """
        Find the unvisited neighbor with the minimum distance.

        :return: address of the neighbor with the minimum distance, or None if all
                 neighbors are visited
        """
        min_dist = float("inf")
        min_neighbor = None
        for neighbor, distance in self._distances.items():
            if not self._visited[neighbor] and distance < min_dist:
                min_dist = distance
                min_neighbor = neighbor
        return min_neighbor

    def mark_visited(self, addr: node_addr_t):
        """
        Mark a node as visited in the Dijkstra algorithm.

        :param addr: address of the node to mark as visited
        """
        self._visited[addr] = True

class DijkstraData:
    """
    Encapsulates a DijkstraDistanceTbl with other state relevant for Dijkstra routing.

    This class should be used for RoutingCube.data.
    """

    def __init__(self, my_addr: node_addr_t):
        """
        Create new Dijkstra data with an empty distance table.

        :param my_addr: address of the node that owns this data
        """
        self.distance_tbl = DijkstraDistanceTbl(my_addr)
        self.last_dv = None # Last distance vector sent by this node
        self.tx_data = None # BMFDataPkt to send from this node

    def new_neighbor(self, addr: node_addr_t, link_cost: int):
        """
        Wrapper for DijkstraDistanceTbl.new_neighbor().
        """
        return self.distance_tbl.new_neighbor(addr, link_cost)

    def update(self, distance_vector: Dict[node_addr_t, int], via: node_addr_t):
        """
        Wrapper for DijkstraDistanceTbl.update().
        """
        return self.distance_tbl.update(distance_vector, via)

    def next_hop(self) -> Optional[node_addr_t]:
        """
        Wrapper for DijkstraDistanceTbl.next_hop().
        """
        return self.distance_tbl.next_hop()

    def mark_visited(self, addr: node_addr_t):
        """
        Mark a node as visited.
        """

class DijkstraRouting(RoutingAlgorithm):
    def __init__(self):
        # Initialize any necessary data structures
        pass

    def route(self, cube: RoutingCube):
        """
        Perform one cycle of Dijkstra's routing.

        :param cube: RoutingCube to operate on
        :raises TypeError: if this cube receives a packet of an invalid type
        :return: cube
        """
        # Get a packet received by the cube
        pkt, rx_dir = cube.get_packet()
        if pkt is not None:
            # Determine the address of the packet sender based on the face it came from
            tx_addr = determine_tx_addr(cube.position, rx_dir)

            if isinstance(pkt, NewNeighborPkt):
                # Cube got notified of a new neighbor node - update routing information
                self.handle_new_neighbor(cube, tx_addr, pkt)
            
            elif isinstance(pkt, DistanceVectorPkt):
                # Cube received distance vector from node - update routing table
                self.update_routing_table(cube, tx_addr, pkt)

            elif isinstance(pkt, DataPkt):
                # Cube received data packet with a destination address
                self.route_packet(cube, pkt)

            else:
                raise TypeError(f"Bad packet type: {type(pkt)}")
            
        # Transmit a packet generated by this cube if one exists
        if cube.data.tx_data is not None:
            self.route_packet(cube, cube.data.tx_data)
            cube.data.tx_data = None
        
        return cube

    def power_on(self, cube: RoutingCube):
        """
        Initialize the cube's routing data and send new neighbor notifications to its
        neighbors.

        :param cube: RoutingCube to operate on
        """
        cube.data = DijkstraData(cube.position)
        #self.send_new_neighbor_notification(cube)

    def send_packet(self, cube: RoutingCube, dest_addr: node_addr_t, data: typing.Any):
        """
        Method used to trigger a packet transmission from this cube to the destination
        node, which will be handled by the routing algorithm.

        :param cube: RoutingCube to operate on
        :param data: packet payload
        :param dest_addr: destination node address
        """
        # Generate data packet with the destination address in this cube
        cube.data.tx_data = DataPkt(dest_addr, data)

    def handle_new_neighbor(self, cube: RoutingCube, neighbor_addr: node_addr_t, pkt: NewNeighborPkt):
        # Handle new neighbor notification
        # Update routing information
        pass

    def update_routing_table(self, cube: RoutingCube, neighbor_addr: node_addr_t, pkt: DistanceVectorPkt):
        # Update routing table based on received distance vector
        pass

    def route_packet(self, cube: RoutingCube, pkt: DataPkt):
        # Route the data packet using Dijkstra's algorithm
        pass


class DijkstraRobot(RobotAlgorithm):
    """
    Robot class with Dijkstra routing algorithm.
    """
    CUBE_ROUTING_ALGO = DijkstraRouting()
    def __init__(self):
        #, addr: int, routing_alg: DijkstraRouting)
        """
        Initialize the robot with its address and routing algorithm.

        :param addr: robot address
        :param routing_algo: routing algorithm instance
        """
        #super().__init__(addr)
        #self.routing_alg = routing_alg
        pass
    

    def step(self, robot: Robot) -> RoutingCube:
        DijkstraRobot.CUBE_ROUTING_ALGO.route(robot.cube)
        

    def power_on(self, robot: Robot):
        DijkstraRobot.CUBE_ROUTING_ALGO.power_on(robot.cube)

"""
# Class representing a node in the graph
class Node:
    def __init__(self, name):
        self.name = name
        self.adjacent = {}
        self.distance = sys.maxsize
        self.visited = False
        self.previous = None

    def add_neighbor(self, neighbor, weight):
        self.adjacent[neighbor] = weight

# Dijkstra algorithm function
def dijkstra(start_node):
    start_node.distance = 0
    # Use a priority queue to keep track of the next node to visit
    priority_queue = [(node.distance, node) for node in graph.values()]
    heapq.heapify(priority_queue)

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_distance > current_node.distance:
            continue

        for neighbor, weight in current_node.adjacent.items():
            distance = current_node.distance + weight
            if distance < neighbor.distance:
                neighbor.distance = distance
                neighbor.previous = current_node
                heapq.heappush(priority_queue, (distance, neighbor))

# Function to get shortest path
def get_shortest_path(target_node):
    path = []
    current_node = target_node
    while current_node:
        path.insert(0, current_node.name)
        current_node = current_node.previous
    return path
"""