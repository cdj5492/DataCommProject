"""
[MD] 4/11/24 Modified Template.route() to use new RoutingCube.get_packet() method.
"""

from network.routing_cube import RoutingCube
from network.faces import Direction
from .routing_algorithm import RoutingAlgorithm

# example of how to use the RoutingAlgorithm class
class Template(RoutingAlgorithm):
    def __init__(self):
        pass

    # Template function for routing algorithms.
    def route(self, cube: RoutingCube):
        # demo routing algorithm just takes the data coming into
        # each face and outputs to the opposite face
        packet, rx_dir = cube.get_packet()

        if packet is not None:
            if rx_dir == Direction.UP:
                cube.send_packet(Direction.DOWN, packet)
            elif rx_dir == Direction.DOWN:
                cube.send_packet(Direction.UP, packet)
            if rx_dir == Direction.NORTH:
                cube.send_packet(Direction.SOUTH, packet)
            elif rx_dir == Direction.SOUTH:
                cube.send_packet(Direction.NORTH, packet)
            if rx_dir == Direction.EAST:
                cube.send_packet(Direction.WEST, packet)
            elif rx_dir == Direction.WEST:
                cube.send_packet(Direction.EAST, packet)
        
        return cube
    
    # do nothing when first powered on for this example
    def power_on(self, cube: RoutingCube) -> None:
        pass

