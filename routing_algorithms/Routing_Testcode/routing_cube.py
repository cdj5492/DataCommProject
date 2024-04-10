from faces import Faces, Direction

class RoutingCube:
    def __init__(self, position: tuple[int, int, int] = (0, 0, 0)) -> None:
        # position of this cube in the lattice
        self.position = position

        # faces of this cube that packets can be sent to
        self.faces = Faces()

        # data stored in this cube for use by routing algorithms
        self.data = None
        
        # references to faces of adjacent cubes
        self.ll_references = Faces(False)
        
    def send_packet(self, direction: Direction, packet):
        # check if the face is connected to another cube
        return self.ll_references.add_packet(direction, packet)
    
    def get_packet(self, direction: Direction):
        return self.faces.get_packet(direction)

    # def set_face(self, direction: Direction, face):
    #     self.faces.set_face(direction, face)

    def step(self, routing_algorithm):
        routing_algorithm.route(self)
    
    def flush_buffers(self):
        self.faces.flush_buffers()
        
    def __repr__(self) -> str:
        packets = [f"{Direction(i).name}: {self.faces.peek_packet(Direction(i))}" for i in range(6)]
        return f"RoutingCube at {self.position}: {packets}"