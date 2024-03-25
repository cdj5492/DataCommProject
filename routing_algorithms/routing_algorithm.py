from ..network.routing_cube import RoutingCube, Faces

# Class that all routing algorithms must inherit from.
class RoutingAlgorithm:
    def __init__(self) -> None:
        pass

    # This function will be called once per routing cube per time step.
    def route(self, cube: RoutingCube) -> RoutingCube:
        pass
    
    # Called once when this cube is first powered on.
    def power_on(self) -> None:
        pass
