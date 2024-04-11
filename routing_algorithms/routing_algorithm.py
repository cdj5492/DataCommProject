"""
[MD] 4/10/24 Added RoutingAlgorithm.send_packet()
"""

from network.routing_cube import RoutingCube

# Class that all routing algorithms must inherit from.
class RoutingAlgorithm:
    def __init__(self) -> None:
        pass

    # This function will be called once per routing cube per time step.
    def route(self, cube: RoutingCube) -> RoutingCube:
        pass
    
    # Called once when this cube is first powered on.
    def power_on(self, cube: RoutingCube) -> None:
        pass

    # Called when a packet transmission needs to be simulated.
    def send_packet(self, cube: RoutingCube, dest_addr, data) -> None:
        pass
