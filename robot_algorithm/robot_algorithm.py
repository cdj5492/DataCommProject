from network.routing_cube import RoutingCube

# Class that all algorithms running on robots must inherit from.
class RobotAlgorithm:
    def __init__(self) -> None:
        pass

    # This function will be called once per robot per time step.
    def step(self, robot: RoutingCube) -> RoutingCube:
        pass

    # Called once when this robot is first powered on (connected to the network)
    def power_on(self, robot: RoutingCube) -> None:
        pass