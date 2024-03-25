from ..network.routing_cube import RoutingCube
from routing_algorithm import RoutingAlgorithm

# example of how to use the RoutingAlgorithm class
class Template(RoutingAlgorithm):
    def __init__(self):
        pass

    # Template function for routing algorithms.
    def route(cube: RoutingCube):
        # demo routing algorithm just takes the data coming into
        # each face and outputs to the opposite face
        
        cube.outgoing.down = cube.incoming.up
        cube.outgoing.up = cube.incoming.down
        
        cube.outgoing.west = cube.incoming.east
        cube.outgoing.east = cube.incoming.west
        
        cube.outgoing.north = cube.incoming.south
        cube.outgoing.south = cube.incoming.north
        return cube
    
    # do nothing when first powered on for this example
    def power_on(self) -> None:
        pass

