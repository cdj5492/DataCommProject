import pprint
import random   

class ThreeD:
    def __init__(self, x, y, z):
        self.x_size = x
        self.y_size = y
        self.z_size = z
        self.lst = [[[None for _ in range(z)] for _ in range(y)] for _ in range(x)]
                            

    def random_populate(self, data):
        for i in range(self.x_size):
            for j in range(self.y_size):
                for k in range(self.z_size):
                    if random.random() < 0.5:
                        self.lst[i][j][k] = data

        self.remove_not_adj()

    def set_element(self, x, y, z, element):
        self.lst[x][y][z] = element
    
    def get_element(self, x, y, z):
        return self.lst[x][y][z]
        
    def remove_element(self, x, y, z):
        self.lst[x][y][z] = None

    def is_neighbor(self, x, y, z):
        # Check if the neighbor exists and if the current cell is within bounds
        up_n = (x > 0 and self.lst[x-1][y][z] is not None)
        down_n = (x < self.x_size - 1 and self.lst[x+1][y][z] is not None)
        north_n = (y > 0 and self.lst[x][y-1][z] is not None)
        south_n = (y < self.y_size - 1 and self.lst[x][y+1][z] is not None)
        east_n = (z > 0 and self.lst[x][y][z-1] is not None)
        west_n = (z < self.z_size - 1 and self.lst[x][y][z+1] is not None)
        return any([up_n, down_n, north_n, south_n, east_n, west_n])

    def remove_not_adj(self):
        for i in range(self.x_size):
            for j in range(self.y_size):
                for k in range(self.z_size):
                    if self.lst[i][j][k] is not None and not self.is_neighbor(i, j, k):
                        self.remove_element(i, j, k)

    def print(self):
        pprint.pprint(self.lst)

# Testing The Class
if __name__ == "__main__":
    arr1 = ThreeD(2, 2, 2)
    arr1.random_populate("RoutingCube")
    arr1.print()
    arr1.remove_not_adj()
    arr1.print()
