"""
[MD] 4/11/24 Removed direction argument from Robot.get_packet() to support single-queue
RoutingCube implementation. Removed newly obsolete method Robot.get_any_packet().
"""

import typing

from .routing_cube import RoutingCube
from .faces import Direction

# robot is just holds a reference to a routing cube it can use to send and receive packets
class Robot:
    def __init__(self, cube: RoutingCube) -> None:
        self.cube = cube
        
    def send_packet(self, direction: Direction, packet):
        return self.cube.send_packet(direction, packet)
    
    def get_packet(self) -> tuple[typing.Any, Direction]|tuple[None, None]:
        return self.cube.get_packet()
    
    def step(self, robot_algorithm):
        robot_algorithm.step(self)
        
    def flush_buffers(self):
        self.cube.flush_buffers()