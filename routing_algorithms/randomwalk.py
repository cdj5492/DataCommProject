"""
[MD] 4/11/24 Modified Template.route() to use new RoutingCube.get_packet() method.
"""

from network.routing_cube import RoutingCube
from network.faces import Direction
from .routing_algorithm import RoutingAlgorithm


from robot_algorithm.robot_algorithm import RobotAlgorithm
from network.robot import Robot
from network.faces import Direction
from dataclasses import dataclass
import random
import dataclasses
from routing_algorithms.helpers import node_addr_t

@dataclasses.dataclass
class GPacket:
    dest_addr : node_addr_t

# example of how to use the RoutingAlgorithm class
class RWRoute(RoutingAlgorithm):
    def __init__(self):
        pass

    # Template function for routing algorithms.
    def route(self, cube: RoutingCube):
        # demo routing algorithm just takes the data coming into
        # each face and outputs to the opposite face
        packet, rx_dir = cube.get_packet()
        connectedDirections = []
        if packet is not None:
            print(packet)
            if cube.id == packet.dest_addr:
                return
            #for d in list(Direction):
             #   if(cube.connected_in_direction(d) is False):
              #      cube.send_packet(d, packet.copy())
            for direction in Direction:
                if cube.connected_in_direction(direction):
                    connectedDirections.append(direction)

            randomDirection = random.choice(connectedDirections)
            cube.send_packet(randomDirection, packet)

        return cube
        # Called when a packet transmission needs to be simulated.
    def send_packet(self, cube: RoutingCube, dest_addr, data) -> None:
        cube.faces.add_packet(GPacket(dest_addr))
        

        
    # do nothing when first powered on for this example
    def power_on(self, cube: RoutingCube) -> None:
        pass



# data stored in a robot 
@dataclass
class RobotData:
    # current step count
    step: int = 0

class RWRobot(RobotAlgorithm):
    def __init__(self) -> None:
        super().__init__()
        
    def step(self, robot: Robot) -> None:
        # demo robot algorithm that just sends sends a packet
        # containing random data out of a random face once every few time steps
        
        if robot.cube.data.step % 2 == 0:
            packetData = random.randint(0, 100)
            #packet = {"data": packetData}
            packet = GPacket(dest_addr=packetData)  # Assuming max_node_address is defined somewhere
            face = random.randint(0, 5)
            robot.send_packet(Direction(face), packet)

        robot.cube.data.step += 1
    
    def power_on(self, robot: Robot) -> None:
        robot.cube.data = RobotData()
        robot.cube.data.step = 0
