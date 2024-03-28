from ..network.routing_cube import RoutingCube
from ..network.faces import Direction
from routing_algorithm import RoutingAlgorithm

# example of how to use the RoutingAlgorithm class
class Template(RoutingAlgorithm):
    def __init__(self):
        pass

    # Template function for routing algorithms.
    def route(cube: RoutingCube):
        # demo routing algorithm just takes the data coming into
        # each face and outputs to the opposite face
        
        packet = cube.get_packet(Direction.UP)
        if packet is not None:
            cube.send_packet(Direction.DOWN, packet)
        packet = cube.get_packet(Direction.DOWN)
        if packet is not None:
            cube.send_packet(Direction.UP, packet)
            
        packet = cube.get_packet(Direction.NORTH)
        if packet is not None:
            cube.send_packet(Direction.SOUTH, packet)
        packet = cube.get_packet(Direction.SOUTH)
        if packet is not None:
            cube.send_packet(Direction.NORTH, packet)
            
        packet = cube.get_packet(Direction.EAST)
        if packet is not None:
            cube.send_packet(Direction.WEST, packet)
        packet = cube.get_packet(Direction.WEST)
        if packet is not None:
            cube.send_packet(Direction.EAST, packet)
        
        return cube
    
    # do nothing when first powered on for this example
    def power_on(self) -> None:
        pass

