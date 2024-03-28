from routing_cube import RoutingCube
from typing import Dict

# class DynamicLattice:
#     def __init__(self, initial_element) -> None:
#         self.lattice = [[[initial_element]]]
        
#         self.center = (0, 0, 0)
        
#     def __position_to_index(self, x: int, y: int, z: int) -> tuple[int, int, int]:
#         return (x + self.center[0], y + self.center[1], z + self.center[2])
        
#     def valid_position(self, x: int, y: int, z: int) -> bool:
#         # transform according to center
#         (x, y, z) = self.__position_to_index(x, y, z)
        
#         return 0 <= x < len(self.lattice[0][0]) and 0 <= y < len(self.lattice[0]) and 0 <= z < len(self.lattice)

#     def get_element(self, x: int, y: int, z: int):
#         if not self.valid_position(x, y, z):
#             return None
#         (x, y, z) = self.__position_to_index(x, y, z)
#         return self.grid[z][y][x]
    
#     def set_element(self, x: int, y: int, z: int, element: RoutingCube):
#         if not self.valid_position(x, y, z):
#             return
#         (x, y, z) = self.__position_to_index(x, y, z)
#         self.grid[z][y][x] = element
        
#     def get_slice(self, z: int):
#         z = z + self.center[2]
#         if z < 0 or z >= len(self.lattice):
#             return None
#         return self.lattice[z]
    
#     # handles resizing the lattice
#     # TODO: very inefficient
#     def add_element(self, x: int, y: int, z: int, element: RoutingCube):
#         (ix, iy, iz) = self.__position_to_index(x, y, z)
#         print("ix: ", ix, " iy: ", iy, " iz: ", iz)
#         if not self.valid_position(x, y, z):
#             if iz < 0:
#                 # add to the front, moving the center as needed
#                 # while len(self.lattice) <= -iz:
#                 for _ in range(-iz):
#                     self.lattice.insert(0, [[None for _ in range(self.width)] for _ in range(self.height)])
#                     self.center = (self.center[0], self.center[1], self.center[2] - iz)
#             else:
#                 while len(self.lattice) <= iz:
#                     self.lattice.append([[None for _ in range(self.width)] for _ in range(self.height)])
            
#             # need to recompute this
#             iz = self.center[2] + z
            
#             if iy < 0:
#                 # while len(self.lattice[iz]) <= -iy:
#                 for _ in range(-iy):
#                     self.lattice[iz].insert(0, [None for _ in range(self.width)])
#                     self.center = (self.center[0], self.center[1] - iy, self.center[2])
#             else:
#                 while len(self.lattice[iz]) <= iy:
#                     self.lattice[iz].append([None for _ in range(self.width)])
            
#             iy = self.center[1] + y
            
#             if ix < 0:
#                 # while len(self.lattice[iz][iy]) <= -ix:
#                 for _ in range(-ix):
#                     self.lattice[iz][iy].insert(0, None)
#                 self.center = (self.center[0] - ix, self.center[1], self.center[2])
#             else:
#                 while len(self.lattice[iz][iy]) <= ix:
#                     self.lattice[iz][iy].append(None)
            
#             ix = self.center[0] + x
            
#         self.lattice[iz][iy][ix] = element
        
#     def remove_element(self, x: int, y: int, z: int) -> RoutingCube:
#         if not self.valid_position(x, y, z):
#             return
#         (x, y, z) = self.__position_to_index(x, y, z)
#         element = self.lattice[z][y][x]
#         self.lattice[z][y][x] = None
#         return element
    
    
# def print_2d(grid):
#     for row in grid:
#         print(row)
    
# # test
# if __name__ == "__main__":
#     lattice = DynamicLattice(None)
#     print_2d(lattice.get_slice(0))
#     lattice.add_element(0, 0, 0, 1)
#     print_2d(lattice.get_slice(0))
#     lattice.add_element(1, 0, 0, 2)
#     print_2d(lattice.get_slice(0))
#     lattice.add_element(-1, 0, 0, 3)
#     print_2d(lattice.get_slice(0))
#     lattice.add_element(0, 1, 0, 4)
#     print_2d(lattice.get_slice(0))
#     lattice.add_element(0, -1, 0, 5)

# grid that uses 2d linked list approach
class NetworkGrid:
    def __init__(self) -> None:
        # Contains pointers to one node in each z layer.
        # Should be the furthest north-west node in the layer.
        self.layer_entry_points: Dict[int, RoutingCube] = {}
        
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
        else:
            # check if it is further north or west than the current entry point
            current_entry = self.layer_entry_points[z]
            if x < current_entry.position[0] or y > current_entry.position[1]:
                self.layer_entry_points[z] = node
            
        # connect references between adjacent nodes
        # z direction
        up = self.get_node(x, y, z+1)
        if up is not None:
            node.ll_references.up = up
            up.ll_references.down = node
        
        down = self.get_node(x, y, z-1)
        if down is not None:
            node.ll_references.down = down
            down.ll_references.up = node
        
        # y direction
        north = self.get_node(x, y+1, z)
        if north is not None:
            node.ll_references.north = north
            north.ll_references.south = node
        
        south = self.get_node(x, y-1, z)
        if south is not None:
            node.ll_references.south = south
            south.ll_references.north = node
        
        # x direction
        east = self.get_node(x+1, y, z)
        if east is not None:
            node.ll_references.east = east
            east.ll_references.west = node
            
        west = self.get_node(x-1, y, z)
        if west is not None:
            node.ll_references.west = west
            west.ll_references.east = node
            
    # returns a 2d array of nodes in the requested z layer.
    # If there are no nodes in that layer, returns None.
    def get_layer(self, z: int) -> list[list[RoutingCube]]:
        # get the entry point
        entry_node = self.layer_entry_points.get(z, None)
        if entry_node is None:
            return None
        
        # traverse the layer. Only works if entry point is the furthest north-west node.
        layer = []
        recursively_get_layer(layer, entry_node)
        
        return layer

    def recursively_get_layer(layer: list[list[RoutingCube]], node: RoutingCube):
        # base case
        if node is None:
            return []
        
        # add this node to the layer if it is not already there
        if len(layer) <= node.position[1]:
            layer.append([None for _ in range(node.position[0] + 1)])
        layer[node.position[1]][node.position[0]] = node