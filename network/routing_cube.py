"""
[MD] 4/11/24 RoutingCube now has a single Queue where packets are stored after being
received on the faces (as opposed to the Faces object having a separate queue for each
Face).
"""

import queue
import typing

from .faces import Faces, Direction


class RoutingCube:
    MAX_Q_LEN = 64

    def __init__(self, position: tuple[int, int, int] = (0, 0, 0)) -> None:
        # position of this cube in the lattice
        self.position = position

        # faces of this cube that packets can be received on
        self.faces = Faces()
        
        # references to faces of adjacent cubes
        self.ll_references = Faces(create_faces=False)

        # queue for packets received by this cube
        self._packets = queue.Queue(maxsize=RoutingCube.MAX_Q_LEN)

        # custom data stored in this cube for use by routing algorithms
        self.data = None

        # Network diagnostic information specific to this cube
        self.num_pkts_received = 0
        self.num_pkts_dropped = 0
        self.highest_q_len = 0
        
    def send_packet(self, direction: Direction, packet):
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
            self.num_pkts_received += 1
            try:
                self._packets.put_nowait(pkt)
            except queue.Full:
                # Packet lost
                self.num_pkts_dropped += 1

            # Track highest recorded queue length
            q_len = self._packets.qsize()
            if q_len > self.highest_q_len:
                self.highest_q_len = q_len
        
    def __repr__(self) -> str:
        packets = [f"{Direction(i).name}: {self.faces.face_has_packet(Direction(i))}" for i in range(6)]
        return f"RoutingCube at {self.position}: {packets}"