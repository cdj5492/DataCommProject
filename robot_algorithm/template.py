from .robot_algorithm import RobotAlgorithm
from network.robot import Robot
from dataclasses import dataclass
import random

# data stored in a robot 
@dataclass
class RobotData:
    # current step count
    step: int = 0

class Template(RobotAlgorithm):
    def __init__(self) -> None:
        super().__init__()
        
    def step(self, robot: Robot) -> None:
        # demo robot algorithm that just sends sends a packet
        # containing random data out of a random face once every 10 time steps
        
        if robot.cube.data.step % 10 == 0:
            packetData = random.randint(0, 100)
            packet = {"data": packetData}
            face = random.randint(0, 5)
            robot.send_packet(face, packet)

        robot.cube.data.step += 1
    
    def power_on(self, robot: Robot) -> None:
        robot.cube.data = RobotData()
        robot.cube.data.step = 0