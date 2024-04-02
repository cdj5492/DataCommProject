from enum import Enum
from queue import Queue

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
        self.buffered_packets = Queue()
    
    def add_packet(self, packet):
        self.buffered_packets.put(packet)
        
    def flush_buffer(self):
        while not self.buffered_packets.empty():
            self.packets.put(self.buffered_packets.get())
    
    def get_packet(self):
        try:
            return self.packets.get_nowait()
        except:
            return None
    
    def peek_packet(self):
        try:
            return self.packets.queue[0]
        except:
            return None

class Faces:
    def __init__(self, create_faces: bool=True) -> None:
        if create_faces:
            self.faces = [Face() for _ in range(6)]
        else:
            self.faces = [None for _ in range(6)]
        
    def add_packet(self, direction: Direction, packet):
        # check that the face exists
        if self.faces[direction.value] is not None:
            self.faces[direction.value].add_packet(packet)
            return True
        return False
    
    def get_packet(self, direction: Direction):
        return self.faces[direction.value].get_packet()

    def peek_packet(self, direction: Direction):
        return self.faces[direction.value].peek_packet()

    def get_face(self, direction: Direction):
        return self.faces[direction.value]

    def set_face(self, direction: Direction, face: Face):
        self.faces[direction.value] = face
    
    def flush_buffers(self):
        for face in self.faces:
            face.flush_buffer()

