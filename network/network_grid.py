"""
[MD] 4/10/24 Added NetworkGrid.send_packet()
[MD] 4/16/24 Modified NetworkGrid.send_packet() and added get_node_by_id(),
remove_node_by_id(), and send_packet_by_coords(). Added id argument to add_node() and
add_robot().
[MD] 4/19/24 Added NetworkGrid.stats attribute for storing NetworkDiagnostics and
NetworkGrid.update_net_stats() for tracking network statistics.
[MD] 4/22/24 Modified NetworkGrid.send_packet() to use the robot_algorithm to do the
sending if the source node belongs to a robot.
"""

from .routing_cube import RoutingCube
from .faces import Direction
from typing import Dict
from network.netstats import NetworkDiagnostics
from routing_algorithms.routing_algorithm import RoutingAlgorithm
from robot_algorithm.robot_algorithm import RobotAlgorithm
from .robot import Robot

# grid that uses 2d linked list approach
class NetworkGrid:
    def __init__(self, routing_algorithm: RoutingAlgorithm, robot_algorithm: RobotAlgorithm)-> None:
        # Contains pointers to one node in each z layer.
        # Should be the furthest north-west node in the layer.
        self.layer_entry_points: Dict[int, RoutingCube] = {}
        
        # list of max and min x and y values for each layer
        self.layer_bounds: Dict[int, tuple[int, int, int, int]] = {}
        
        # Allows lookup of node by position
        self.node_map: Dict[tuple[int, int, int], RoutingCube] = {}
        
        # List of all nodes in the network
        self.node_list = []
    
        # List of all robots in the network
        self.robot_list = []

        self.routing_algorithm = routing_algorithm
        self.robot_algorithm = robot_algorithm

        self.stats = NetworkDiagnostics()
    
    # Gets the requested node from the network.
    # Returns None if the node does not exist.
    def get_node(self, x: int, y: int, z: int) -> RoutingCube:
        return self.node_map.get((x, y, z), None)
    
    def get_node_by_id(self, id:int|str) -> RoutingCube|None:
        for node in self.node_list:
            if node.id == id:
                return node
        return None
        
    def add_robot(self, x: int, y: int, z: int, id:int|str|None=None):
        node = RoutingCube((x, y, z), id)
        robot = Robot(node)
        
        self.robot_list.append(robot)
        
        self.add_node(x, y, z, id, node)
        
        # power on
        self.robot_algorithm.power_on(robot)
    
    def add_node(self, x: int, y: int, z: int, id:int|str|None=None, node: RoutingCube = None):
        if node is None:
            node = RoutingCube((x, y, z), id)

        # put it in the node_map
        self.node_map[(x, y, z)] = node
    
        self.node_list.append(node)
        
        # check if this layer exists
        if z not in self.layer_entry_points.keys():
            # add it as an entry point
            self.layer_entry_points[z] = node
            self.layer_bounds[z] = (x, x, y, y)
        else:
            # check if it is further north or west than the current entry point
            current_entry = self.layer_entry_points[z]
            if x < current_entry.position[0] or y > current_entry.position[1]:
                self.layer_entry_points[z] = node
            
            # update the bounds
            min_x, max_x, min_y, max_y = self.layer_bounds[z]
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
            self.layer_bounds[z] = (min_x, max_x, min_y, max_y)
            
        # connect references between adjacent nodes
        # z direction
        up = self.get_node(x, y, z+1)
        if up is not None:
            up.ll_references.set_face(Direction.DOWN, node.faces.get_face(Direction.UP))
            node.ll_references.set_face(Direction.UP, up.faces.get_face(Direction.DOWN))
        
        down = self.get_node(x, y, z-1)
        if down is not None:
            down.ll_references.set_face(Direction.UP, node.faces.get_face(Direction.DOWN))
            node.ll_references.set_face(Direction.DOWN, down.faces.get_face(Direction.UP))
        
        # y direction
        north = self.get_node(x, y+1, z)
        if north is not None:
            north.ll_references.set_face(Direction.SOUTH, node.faces.get_face(Direction.NORTH))
            node.ll_references.set_face(Direction.NORTH, north.faces.get_face(Direction.SOUTH))
            
        south = self.get_node(x, y-1, z)
        if south is not None:
            south.ll_references.set_face(Direction.NORTH, node.faces.get_face(Direction.SOUTH))
            node.ll_references.set_face(Direction.SOUTH, south.faces.get_face(Direction.NORTH))
            
        # x direction
        east = self.get_node(x+1, y, z)
        if east is not None:
            east.ll_references.set_face(Direction.WEST, node.faces.get_face(Direction.EAST))
            node.ll_references.set_face(Direction.EAST, east.faces.get_face(Direction.WEST))
            
        west = self.get_node(x-1, y, z)
        if west is not None:
            west.ll_references.set_face(Direction.EAST, node.faces.get_face(Direction.WEST))
            node.ll_references.set_face(Direction.WEST, west.faces.get_face(Direction.EAST))
        
        # run power on code for the node
        self.routing_algorithm.power_on(node)
    
    def remove_node(self, x: int, y: int, z: int):
        # get the node
        node = self.get_node(x, y, z)
        if node is None:
            return
        
        # remove it from the node map
        self.node_map.pop((x, y, z))
        
        self.node_list.remove(node)
        
        # remove linked list references
        # z direction
        up = self.get_node(x, y, z+1)
        if up is not None:
            up.ll_references.set_face(Direction.DOWN, None)
        down = self.get_node(x, y, z-1)
        if down is not None:
            down.ll_references.set_face(Direction.UP, None)
            
        # y direction
        north = self.get_node(x, y+1, z)
        if north is not None:
            north.ll_references.set_face(Direction.SOUTH, None)
        south = self.get_node(x, y-1, z)
        if south is not None:
            south.ll_references.set_face(Direction.NORTH, None)
            
        # x direction
        east = self.get_node(x+1, y, z)
        if east is not None:
            east.ll_references.set_face(Direction.WEST, None)
        west = self.get_node(x-1, y, z)
        if west is not None:
            west.ll_references.set_face(Direction.EAST, None)

    def remove_node_by_id(self, id:int|str):
        node = self.get_node_by_id(id)
        if node is None:
            return
        self.remove_node(*node.position)
            
    # returns a 2d array of nodes in the requested z layer.
    # If there are no nodes in that layer, returns None.
    def get_layer(self, z: int) -> list[list[RoutingCube]]:
        # get the entry point
        entry_node = self.layer_entry_points.get(z, None)
        if entry_node is None:
            return None
        
        # get the bounds
        min_x, max_x, min_y, max_y = self.layer_bounds[z]
        # create the array to fit the bounds
        layer = [[None for _ in range(min_x, max_x+1)] for _ in range(min_y, max_y+1)]
        
        # fill the array by traversing all elements of 
        # the linked list, ignoring nodes that have already been visited.
        # This algorithm is called a depth-first search.
        x, y, _ = entry_node.position
        visited = set()
        stack = [(x, y)]
        while len(stack) > 0:
            x, y = stack.pop()
            if x < min_x or x > max_x or y < min_y or y > max_y:
                continue
            if (x, y) in visited:
                continue
            visited.add((x, y))
            node = self.get_node(x, y, z)
            if node is None:
                continue
            layer[y - min_y][x - min_x] = node
            stack.append((x+1, y))
            stack.append((x-1, y))
            stack.append((x, y+1))
            stack.append((x, y-1))

        return layer
    
    def get_all_nodes(self) -> list[RoutingCube]:
        return self.node_list
    
    def update_net_stats(self):
        self.stats.reset_cycle_dependent_stats()
        for node in self.node_list:
            self.stats.integrate_node_stats(node.stats)
    
    def step(self):
        for node in self.node_list:
            node.step(self.routing_algorithm)
        
        for node in self.node_list:
            node.flush_buffers()
            
        for robot in self.robot_list:
            robot.step(self.robot_algorithm)

        self.update_net_stats()

    def send_packet(self, data, src_id:int|str, dest_id:int|str):
        src_node = self.get_node_by_id(src_id)
        if src_node is None:
            raise ValueError(f"Cannot trigger packet transmission from node ID:'{src_id}'; Node does not exist")
        
        if src_node.stats.is_robot:
            for robot in self.robot_list:
                if robot.cube.id == src_node.id:
                    self.robot_algorithm.send_packet(robot, dest_id, data)
                    break
        else:
            self.routing_algorithm.send_packet(src_node, dest_id, data)

    def send_packet_by_coords(self, data, src_coords:tuple[int,int,int], dest_coords:tuple[int,int,int]):
        # Retrieves the source node and calls the routing algorithm to trigger packet transmission
        src_node = self.get_node(*src_coords)
        dest_node = self.get_node(*dest_coords)
        if src_node is None:
            raise ValueError(f"Cannot trigger packet transmission from src node {src_coords}; Node does not exist")
        if dest_node is None:
            dest_id = RoutingCube._ID_NODE_DNE
        else:
            dest_id = dest_node.id
        self.routing_algorithm.send_packet(src_node, dest_id, data)
