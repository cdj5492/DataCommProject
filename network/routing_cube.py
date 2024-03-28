class Faces:
    def __init__(self) -> None:
        self.up = None
        self.down = None
        self.west = None
        self.east = None
        self.north = None
        self.south = None

class RoutingCube:
    def __init__(self, position: tuple[int, int, int] = (0, 0, 0)) -> None:
        # position of this cube in the lattice
        self.position = position

        self.incoming = Faces()
        self.outgoing = Faces()

        # data stored in this cube for use by routing algorithms
        self.data = None
        
        # for use by simulator, not routing algorithms
        self.ll_references = Faces()