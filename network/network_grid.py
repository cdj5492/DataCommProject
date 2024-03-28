from routing_cube import RoutingCube
from faces import Direction
from typing import Dict

# grid that uses 2d linked list approach
class NetworkGrid:
    def __init__(self) -> None:
        # Contains pointers to one node in each z layer.
        # Should be the furthest north-west node in the layer.
        self.layer_entry_points: Dict[int, RoutingCube] = {}
        
        # list of max and min x and y values for each layer
        self.layer_bounds: Dict[int, tuple[int, int, int, int]] = {}
        
        # Allows lookup of node by position
        self.node_map: Dict[tuple[int, int, int], RoutingCube] = {}
    
    # Gets the requested node from the network.
    # Returns None if the node does not exist.
    def get_node(self, x: int, y: int, z: int) -> RoutingCube:
        return self.node_map.get((x, y, z), None)
        
    def add_node(self, x: int, y: int, z: int, node: RoutingCube):
        # put it in the node_map
        self.node_map[(x, y, z)] = node
        
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
            up.set_face(Direction.DOWN, node.ll_references.get_face(Direction.UP))
            node.set_face(Direction.UP, up.ll_references.get_face(Direction.DOWN))
        
        down = self.get_node(x, y, z-1)
        if down is not None:
            down.set_face(Direction.UP, node.ll_references.get_face(Direction.DOWN))
            node.set_face(Direction.DOWN, down.ll_references.get_face(Direction.UP))
        
        # y direction
        north = self.get_node(x, y+1, z)
        if north is not None:
            north.set_face(Direction.SOUTH, node.ll_references.get_face(Direction.NORTH))
            node.set_face(Direction.NORTH, north.ll_references.get_face(Direction.SOUTH))
            
        south = self.get_node(x, y-1, z)
        if south is not None:
            south.set_face(Direction.NORTH, node.ll_references.get_face(Direction.SOUTH))
            node.set_face(Direction.SOUTH, south.ll_references.get_face(Direction.NORTH))
            
        # x direction
        east = self.get_node(x+1, y, z)
        if east is not None:
            east.set_face(Direction.WEST, node.ll_references.get_face(Direction.EAST))
            node.set_face(Direction.EAST, east.ll_references.get_face(Direction.WEST))
            
        west = self.get_node(x-1, y, z)
        if west is not None:
            west.set_face(Direction.EAST, node.ll_references.get_face(Direction.WEST))
            node.set_face(Direction.WEST, west.ll_references.get_face(Direction.EAST))
        
            
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