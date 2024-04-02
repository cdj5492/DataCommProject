from network.network_grid import NetworkGrid
from network.faces import Direction
from routing_algorithms.template import Template

def print_grid(grid):
    grid_nodes = grid.get_all_nodes()
    for node in grid_nodes:
        print(node)

# test code
if __name__ == '__main__':
    # main grid
    grid = NetworkGrid(Template())
    
    # add some nodes to the grid
    grid.add_node(0, 0, 0)
    grid.add_node(1, 0, 0)
    grid.add_node(1, 1, 0)
    grid.add_node(2, 0, 0)
    
    grid.get_node(2, 0, 0).send_packet(Direction.WEST, "Hello")
    
    # step it a few times
    for _ in range(5):
        print_grid(grid)
        print()
        grid.step()
    
    print_grid(grid)