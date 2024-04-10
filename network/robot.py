from .routing_cube import RoutingCube
from .faces import Direction

# robot is just holds a reference to a routing cube it can use to send and receive packets
class Robot:
    def __init__(self, cube: RoutingCube) -> None:
        self.cube = cube
        
    def send_packet(self, direction: Direction, packet):
        return self.cube.send_packet(direction, packet)
    
    def get_packet(self, direction):
        return self.cube.get_packet(direction)
    
    def get_any_packet(self):
        for i in range(6):
            packet = self.get_packet(i)
            if packet is not None:
                return packet
        return None
    
    def step(self, robot_algorithm):
        robot_algorithm.step(self)
        
    def flush_buffers(self):
        self.cube.flush_buffers()