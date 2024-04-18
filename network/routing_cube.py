"""
[MD] 4/11/24 RoutingCube now has a single Queue where packets are stored after being
received on the faces (as opposed to the Faces object having a separate queue for each
Face).
[MD] 4/14/24 Added NodeDiagnostics class for tracking RoutingCube statistics at runtime.
[MD] 4/16/24 RoutingCube IDs implemented.
"""

import dataclasses
import queue
import typing

from .faces import Faces, Direction


@dataclasses.dataclass
class NodeDiagnostics:
    num_pkts_sent : int = 0
    num_pkts_received : int = 0
    num_pkts_dropped : int = 0
    highest_q_len : int = 0
    is_robot : bool = False
    has_packet : bool = False


    def get_num_pkts_sent(self) -> int:
        return self.num_pkts_sent
    

    def get_num_pkts_received(self) -> int:
        return self.num_pkts_received
    

    def get_num_pkts_dropped(self) -> int:
        return self.num_pkts_dropped
    

    def get_highest_q_len(self) -> int:
        return self.highest_q_len
    

    def get_is_robot(self) -> bool:
        return self.is_robot
    

    def get_has_packet(self) -> bool:
        return self.has_packet


class RoutingCube:
    _NEXT_ID = 0
    _ID_NODE_DNE = -1
    MAX_Q_LEN = 64

    def __init__(self, position: tuple[int, int, int] = (0, 0, 0), id:int|str|None=None) -> None:
        # position of this cube in the lattice
        self.position = position

        # Unique ID ("MAC address") for this cube
        if id is None:
            self.id = RoutingCube._NEXT_ID
            RoutingCube._NEXT_ID += 1
        else:
            self.id = id

        # faces of this cube that packets can be received on
        self.faces = Faces()
        
        # references to faces of adjacent cubes
        self.ll_references = Faces(create_faces=False)

        # queue for packets received by this cube
        self._packets = queue.Queue(maxsize=RoutingCube.MAX_Q_LEN)

        # custom data stored in this cube for use by routing algorithms
        self.data = None

        # Network diagnostic information tracked by this cube
        self._stats = NodeDiagnostics()

    @property
    def stats(self) -> NodeDiagnostics:
        self._stats.has_packet = self.has_packet()
        return self._stats
    
    @stats.setter
    def stats(self, value:NodeDiagnostics):
        self._stats = value
    
    def connected_in_direction(self, direction: Direction) -> bool:
        #         # technically, real cubes wouldn't have access to this, but 
        #         # real hardware could determine this information electrically
        return self.ll_references.faces[direction.value] is not None
        # match direction:
        #     case Direction.UP:
        #         # technically, real cubes wouldn't have access to this, but 
        #         # real hardware could determine this information electrically
        #         return self.ll_references.faces[Direction.DOWN.value] is not None
        #     case Direction.DOWN:
        #         return self.ll_references.faces[Direction.UP.value] is not None
        #     case Direction.WEST:
        #         return self.ll_references.faces[Direction.EAST.value] is not None
        #     case Direction.EAST:
        #         return self.ll_references.faces[Direction.WEST.value] is not None
        #     case Direction.NORTH:
        #         return self.ll_references.faces[Direction.SOUTH.value] is not None
        #     case Direction.SOUTH:
        #         return self.ll_references.faces[Direction.NORTH.value] is not None
        #     case _:
        #         return False
        
    def send_packet(self, direction: Direction, packet):
        self._stats.num_pkts_sent += 1
        # check if the face is connected to another cube
        return self.ll_references.add_packet(direction, packet)
    
    def get_packet(self) -> tuple[typing.Any, Direction]|tuple[None, None]:
        """
        Gets a tuple consisting of a packet from the front of the queue and a direction
        representing the cube face that packet was received on.

        :return: packet, RX direction
        """
        if not self._packets.empty():
            return self._packets.get_nowait()
        else:
            return None, None
        
    def has_packet(self) -> bool:
        return not self._packets.empty()

    # def set_face(self, direction: Direction, face):
    #     self.faces.set_face(direction, face)

    def step(self, routing_algorithm):
        # Perform routing actions
        routing_algorithm.route(self)
    
    def flush_buffers(self):
        # Receive packets on all faces and place in queue
        received = self.faces.get_all_packets()

        for pkt in received:
            self._stats.num_pkts_received += 1
            try:
                self._packets.put_nowait(pkt)
            except queue.Full:
                # Packet lost
                self._stats.num_pkts_dropped += 1

            # Track highest recorded queue length
            q_len = self._packets.qsize()
            if q_len > self._stats.highest_q_len:
                self._stats.highest_q_len = q_len
        
    def __repr__(self) -> str:
        return f"RoutingCube at {self.position}: (data: {self.data})"