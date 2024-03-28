from enum import Enum
from queue import Queue
from routing_cube import RoutingCube

class Direction(Enum):
    UP = 0
    DOWN = 1
    WEST = 2
    EAST = 3
    NORTH = 4
    SOUTH = 5

class Face:
    def __init__(self) -> None:
        self.packets = Queue()
    
    def add_packet(self, packet):
        self.packets.put(packet)
    
    def get_packet(self):
        try:
            return self.packets.get_nowait()
        except:
            return None

class Faces:
    def __init__(self) -> None:
        self.faces = [Face() for _ in range(6)]
        
    def add_packet(self, direction: Direction, packet):
        self.faces[direction.value].add_packet(packet)
    
    def get_packet(self, direction: Direction):
        return self.faces[direction.value].get_packet()

    def get_face(self, direction: Direction):
        return self.faces[direction.value]

    def set_face(self, direction: Direction, face: Face):
        self.faces[direction.value] = face

