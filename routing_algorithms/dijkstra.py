import dataclasses
from typing import Dict, Optional

from network.robot import Robot
from network.routing_cube import RoutingCube
from network.faces import Direction
from robot_algorithm.robot_algorithm import RobotAlgorithm
from routing_algorithms.helpers import node_addr_t, determine_tx_dir, determine_tx_addr


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

class DijkstraRouting(RobotAlgorithm):
    """
    Dijkstra routing algorithm implementation.
    """

    def __init__(self):
        #, robot: Robot, cube: RoutingCube
        """
        Initialize the routing algorithm with the robot and routing cube.

        :param robot: robot instance (default: None)
        :param cube: routing cube instance (default: None)
        """
        #super().__init__(robot, cube)  # Pass arguments to RobotAlgorithm
        pass
    def power_on(self, cube: RoutingCube) -> None:
        """
        Called when the routing algorithm is powered on.

        :param cube: routing cube instance
        """
        cube.data = DijkstraData(cube.position)

    def route(self, cube: RoutingCube) -> None:
        """
        Perform a routing step based on the Dijkstra algorithm.

        This function should use the robot and routing cube to exchange routing
        information, update the distance table, and potentially transmit data packets.

        :param robot: robot instance
        """
        # 1. Receive packets from neighbors
        routing_packets = cube.recv_packets(robot)
        # 2. Update distance table based on received packets (using data.update())
        for packet in routing_packets:
            self.data.update(packet.distance_vector, packet.source)

        # 3. If there's a packet to deliver, determine next hop using data.next_hop()
        if self.has_packet_to_deliver():
            next_hop = self.data.next_hop()
            if next_hop:
                # 4. Transmit packet to the next hop using robot.transmit()
                self.robot.transmit(self.get_packet_to_deliver(), determine_tx_dir(next_hop))

        # 5. Mark visited nodes (optional, might be handled implicitly)

    def has_packet_to_deliver(self) -> bool:
        """
        Check if the robot has a packet to deliver based on its routing table.

        :return: True if the robot has a packet to deliver, False otherwise
        """
        # Implement logic to check if the robot has a packet for a destination
        # that can be reached based on the current distance table
        pass

class DijkstraRobot(Robot):
    """
    Robot class with Dijkstra routing algorithm.
    """

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
    
    def power_on(self, cube: RoutingCube) -> None:
        """
        Power on the robot and its routing algorithm.

        :param cube: routing cube instance
        """
        #self.routing_alg.power_on(cube)
        pass

    def step(self) -> None:
        """
        Perform a routing step based on the robot's routing algorithm.
        """
        #self.routing_alg.step(self)
        pass

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