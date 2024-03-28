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
        self.ll_references = Faces()
        
    def send_packet(self, direction: Direction, packet):
        self.ll_references.add_packet(direction, packet)
    
    def get_packet(self, direction: Direction):
        return self.faces.get_packet(direction)