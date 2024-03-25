from routing_cube import RoutingCube

class DynamicLattice:
    def __init__(self, initial_element) -> None:
        self.lattice = [[[initial_element]]]
        
        self.center = (0, 0, 0)
        
    def __position_to_index(self, x: int, y: int, z: int) -> tuple[int, int, int]:
        return (x + self.center[0], y + self.center[1], z + self.center[2])
        
    def valid_position(self, x: int, y: int, z: int) -> bool:
        # transform according to center
        (x, y, z) = self.__position_to_index(x, y, z)
        
        return 0 <= x < len(self.lattice[0][0]) and 0 <= y < len(self.lattice[0]) and 0 <= z < len(self.lattice)

    def get_element(self, x: int, y: int, z: int):
        if not self.valid_position(x, y, z):
            return None
        (x, y, z) = self.__position_to_index(x, y, z)
        return self.grid[z][y][x]
    
    def set_element(self, x: int, y: int, z: int, element: RoutingCube):
        if not self.valid_position(x, y, z):
            return
        (x, y, z) = self.__position_to_index(x, y, z)
        self.grid[z][y][x] = element
        
    def get_slice(self, z: int):
        z = z + self.center[2]
        if z < 0 or z >= len(self.lattice):
            return None
        return self.lattice[z]
    
    # handles resizing the lattice
    # TODO: very inefficient
    def add_element(self, x: int, y: int, z: int, element: RoutingCube):
        (ix, iy, iz) = self.__position_to_index(x, y, z)
        if not self.valid_position(x, y, z):
            if iz < 0:
                # add to the front, moving the center as needed
                while 
            else:
                while len(self.lattice) < iz:
                    self.lattice.append([[None for _ in range(self.width)] for _ in range(self.height)])
            
        (x, y, z) = self.__position_to_index(x, y, z)
        self.lattice[z][y][x] = element