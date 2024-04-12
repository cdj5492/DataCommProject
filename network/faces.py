"""
[MD] 4/11/24 Reworked Face and Faces for single-queue RoutingCube.
"""

from enum import Enum
import typing

class Direction(Enum):
    UP = 0
    DOWN = 1
    WEST = 2
    EAST = 3
    NORTH = 4
    SOUTH = 5

class Face:
    def __init__(self) -> None:
        self._rx_buffer = list()

    def buffer_pkt(self, packet:typing.Any):
        self._rx_buffer.append(packet)

    def get_buffered_pkts(self) -> list[typing.Any]:
        pkts = self._rx_buffer.copy()
        self._rx_buffer.clear()
        return pkts
    
    def has_pkt(self) -> bool:
        return len(self._rx_buffer) > 0

class Faces:
    def __init__(self, create_faces: bool=True) -> None:
        if create_faces:
            self.faces = [Face() for _ in range(6)]
        else:
            self.faces = [None for _ in range(6)]
        
    def add_packet(self, direction: Direction, packet):
        # check that the face exists
        if self.faces[direction.value] is not None:
            self.faces[direction.value].buffer_pkt(packet)
            return True
        return False
    
    def get_face_packet(self, direction: Direction):
        return self.faces[direction.value].pkt_rx

    def face_has_packet(self, direction: Direction) -> bool:
        return self.faces[direction.value].has_pkt()
    
    def get_all_packets(self) -> list[tuple[typing.Any, Direction]]:
        packets = list()
        for dir, face in enumerate(self.faces):
            for pkt in face.get_buffered_pkts():
                packets.append((pkt, Direction(dir)))
        return packets
    
    def has_packet(self) -> bool:
        return any([face.has_pkt() for face in self.faces])

    def get_face(self, direction: Direction):
        return self.faces[direction.value]

    def set_face(self, direction: Direction, face: Face):
        self.faces[direction.value] = face
