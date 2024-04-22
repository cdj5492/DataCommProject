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
from routing_algorithms.helpers import node_addr_t, node_pos_t, determine_tx_dir, determine_tx_pos
from routing_algorithms.routing_algorithm import RoutingAlgorithm

RP_DEFAULT_LINK_COST = 1

MAX_PACKET_IDS = 10

class Path:
    def __init__(self, path: list[Direction]):
        self.path = path
        # where in the path routing currently is
        self.path_pos = 0
        
        self.reversed = False
    
    def next(self):
        if self.path_pos >= len(self.path) or self.path_pos < 0:
            return None
        
        ret_val = self.path[self.path_pos]

        if self.reversed:
            self.path_pos -= 1
        else:
            self.path_pos += 1
        
        return ret_val
    
    def copy(self):
        copied = Path(self.path.copy())
        copied.path_pos = self.path_pos
        copied.reversed = self.reversed
        return copied
    
    def __repr__(self) -> str:
        return f"Path(path={self.path}, path_pos={self.path_pos}, reversed={self.reversed})"

@dataclasses.dataclass
class RequestPositionPkt:
    """
    Requests the position of whatever node receives this packet
    """
    
    # phantom field to make this class a valid dataclass
    _phantom: int = 0
    
@dataclasses.dataclass
class NeighborPositionPkt:
    """
    Contains the position of a neighboring node.
    """
    position: tuple[int, int, int]

@dataclasses.dataclass
class NetNodeData:
    """
    Encapsulates all data used by a node in the network.

    This class should be used for RoutingCube.data.
    """
    position: tuple[int, int, int] = (0, 0, 0)
    position_known: bool = False
    
    pending_position_requests: list[Direction] = dataclasses.field(default_factory=list)
    
    previously_received_packet_ids: list[int] = dataclasses.field(default_factory=list)
    
    def __repr__(self) -> str:
        return f"NetNodeData(position={self.position}, position_known={self.position_known})"

@dataclasses.dataclass
class NetworkShapeRequestPkt:
    id: int = 0
    # path_taken: list[Direction] = dataclasses.field(default_factory=list)
    path_taken: Path = Path([])

@dataclasses.dataclass
class NetworkShapeResponsePkt:
    # path_to_take: list[Direction] = dataclasses.field(default_factory=list)
    path_to_take: Path = Path([])
    node_position: tuple[int, int, int] = (0, 0, 0)
    
@dataclasses.dataclass
class RobotData:
    id: int = 0
    tmp: int = 0

class Graph:
    def __init__(self):
        self.graph = {}

    def add_edge(self, node1, node2, cost):
        if node1 not in self.graph:
            self.graph[node1] = []
        if node2 not in self.graph:
            self.graph[node2] = []

        self.graph[node1].append((node2, cost))
        self.graph[node2].append((node1, cost))  # For bidirectional graph
    
    def add_node(self, node):
        if node not in self.graph:
            self.graph[node] = []

        # check for nodes around this node and add edges
        for direction in Direction:
            neighbor = determine_tx_pos(node, direction)
            if neighbor is not None:
                self.add_edge(node, neighbor, RP_DEFAULT_LINK_COST)

    def get_neighbors(self, node):
        if node in self.graph:
            return self.graph[node]
        return []
    

def reverse_direction(direction:Direction) -> Direction:
    match direction:
        case Direction.UP:
            return Direction.DOWN
        case Direction.DOWN:
            return Direction.UP
        case Direction.WEST:
            return Direction.EAST
        case Direction.EAST:
            return Direction.WEST
        case Direction.NORTH:
            return Direction.SOUTH
        case Direction.SOUTH:
            return Direction.NORTH
        case _:
            return direction

class NetNodeRouting(RoutingAlgorithm):
    def __init__(self):
        pass
    
    def route(self, cube:RoutingCube):
        
        # attempt to process any pending position requests
        if cube.data.position_known and len(cube.data.pending_position_requests) > 0:
            for direction in cube.data.pending_position_requests:
                cube.send_packet(direction, NeighborPositionPkt(cube.data.position))
            cube.data.pending_position_requests.clear()
        
        # if there are packets in the queue, process them
        for packet in cube.faces.get_all_packets():
            print(f"Node {cube.id} received packet {packet[0]} from direction {packet[1]}")
            if isinstance(packet[0], RequestPositionPkt):
                if not cube.data.position_known:
                    cube.data.pending_position_requests.append(packet[1])
                else:
                    # send a response packet with this node's position in the direction it came from
                    cube.send_packet(packet[1], NeighborPositionPkt(cube.data.position))
                    print(f"Node {cube.id} sent position response to direction {packet[1]}")

            elif isinstance(packet[0], NeighborPositionPkt):
                # determine my position relative to the neighbor
                neighbor_pos = packet[0].position
                neighbor_dir = packet[1]
                match neighbor_dir:
                    # if neighbor is above me, I am below it
                    case Direction.UP:
                        cube.data.position = (neighbor_pos[0], neighbor_pos[1], neighbor_pos[2] - 1)
                    case Direction.DOWN:
                        cube.data.position = (neighbor_pos[0], neighbor_pos[1], neighbor_pos[2] + 1)
                    case Direction.WEST:
                        cube.data.position = (neighbor_pos[0] + 1, neighbor_pos[1], neighbor_pos[2])
                    case Direction.EAST:
                        cube.data.position = (neighbor_pos[0] - 1, neighbor_pos[1], neighbor_pos[2])
                    case Direction.NORTH:
                        cube.data.position = (neighbor_pos[0], neighbor_pos[1] + 1, neighbor_pos[2])
                    case Direction.SOUTH:
                        cube.data.position = (neighbor_pos[0], neighbor_pos[1] - 1, neighbor_pos[2])
                    case _: # default case
                        pass
                cube.data.position_known = True

            elif isinstance(packet[0], NetworkShapeRequestPkt):
                # check if I know my own position
                if not cube.data.position_known:
                    # put packet back in the queue
                    cube.faces.add_packet(packet[1], packet[0])
                    continue

                # check if this packet has been received before (avoid loops)
                if packet[0].id not in cube.data.previously_received_packet_ids:
                    # add it
                    cube.data.previously_received_packet_ids.append(packet[0].id)
                    # if the list is too long, remove the oldest packet
                    if len(cube.data.previously_received_packet_ids) > MAX_PACKET_IDS:
                        cube.data.previously_received_packet_ids.pop(0)
                    
                    # create a copy of the packet
                    new_packet = NetworkShapeRequestPkt(packet[0].id)
                    new_packet.path_taken = packet[0].path_taken.copy()
                    new_packet.path_taken.reversed = True
                    new_packet.path_taken.path_pos = len(new_packet.path_taken.path) - 1
                    
                    # send a packet back in the direction it came from
                    cube.send_packet(packet[1], NetworkShapeResponsePkt(new_packet.path_taken))
                    
                    # add direction packet came from to path_taken
                    new_packet.path_taken.path.append(packet[1])
                    
                    # send packet in all directions except the one it came from
                    for direction in Direction:
                        if direction != packet[1]:
                            cube.send_packet(direction, new_packet)

            elif isinstance(packet[0], NetworkShapeResponsePkt):
                # next_direction = packet[0].path_to_take.pop(0)
                next_direction = packet[0].path_to_take.next()
                if next_direction is not None:
                    cube.send_packet(next_direction, packet[0])
                else:
                    print(f"Packet {packet[0]} dropped")
                

    def power_on(self, cube: RoutingCube):
        cube.data = NetNodeData()
        # request position information from neighboring nodes.
        # if there are no neighbors, assume this node is 
        # the first in the network, and is placed at (0, 0, 0)
        # NOTE: This will fail if multiple seperate networks are
        # connected at some point in the future
        
        # check for neighbors
        no_neighbors = True
        for direction in Direction:
            if cube.connected_in_direction(direction):
                cube.send_packet(direction, RequestPositionPkt())
                print(f"Node {cube.id} sent position request to direction {direction}")
                no_neighbors = False
                break
        if no_neighbors:
            cube.data.position = (0, 0, 0)
            cube.data.position_known = True

    
    def send_packet(self, cube: RoutingCube, dest_addr: node_addr_t, data: typing.Any):
        pass


class RoutePlanningRobot(RobotAlgorithm):
    def __init__(self):
        pass


    def step(self, robot: Robot) -> RoutingCube:
        if robot.data.tmp % 20 == 19:
            packet = NetworkShapeRequestPkt(robot.data.tmp)
            for direction in Direction:
                if robot.cube.connected_in_direction(direction):
                    robot.cube.send_packet(direction, packet)
                    break
                
        for packet in robot.cube.faces.get_all_packets():
            pass

        robot.data.tmp += 1
        

    def power_on(self, robot: Robot):
        robot.cube.data = NetNodeData()
        robot.data = RobotData()
    
        pass
