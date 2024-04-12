import dataclasses
import typing

from network.robot import Robot
from network.routing_cube import RoutingCube
from network.faces import Direction
from robot_algorithm.robot_algorithm import RobotAlgorithm
from routing_algorithms.routing_algorithm import RoutingAlgorithm

node_addr_t: typing.TypeAlias = tuple[int,int,int]


class NewNeighborPkt:
    def __init__(self, link_cost:int=1):
        self.link_cost = link_cost
        self.ack = False


class DistanceVectorPkt:
    def __init__(self, vector:dict[node_addr_t, int]):
        self.vector = vector


@dataclasses.dataclass
class DataPkt:
    dest: node_addr_t
    payload: typing.Any


class DistanceTbl:
    def __init__(self, my_addr:node_addr_t):
        self.my_addr = my_addr
        self.distances = dict()


    def new_neighbor(self, addr:node_addr_t, link_cost:int):
        # Create dict for the neighbor if it is new
        if addr not in self.distances:
            self.distances[addr] = dict()
        # Distance to new neighbor via new neighbor is equal to specified link cost
        self.distances[addr][addr] = link_cost


    def update(self, distance_vector:dict[node_addr_t, int], via:node_addr_t):
        # If the neighbor not is not yet known, add it
        if via not in self.distances:
            self.new_neighbor(via, 1)

        # Iterate over destinations and corresponding distances thru the neighbor node
        for dest, distance in distance_vector.items():
            # Skip destination if it is myself
            if dest != self.my_addr:

                # Create dict for the destination if it is new
                if dest not in self.distances:
                    self.distances[dest] = dict()

                # Distance to destination thru neighbor = distance from neighbor to dest + link cost to neighbor
                link_cost_to_via = self.distances[via][via]
                self.distances[dest][via] = distance + link_cost_to_via

    
    def next_hop(self, dest:node_addr_t) -> node_addr_t|None:
        neighbor = None
        neighbor_cost = 0
        # Determine the neighbor with the minimum link cost to the destination
        if dest in self.distances:
            dest_row = self.distances[dest]
            for via, cost in dest_row.items():
                if neighbor is None or cost < neighbor_cost:
                    neighbor, neighbor_cost = via, cost
        return neighbor
    

    def get_distance_vector(self) -> dict[node_addr_t, int]:
        dv = dict()
        for dest, via_row in self.distances.items():
            dv[dest] = min(via_row.values())
        return dv


class BellmanFordData:
    def __init__(self, my_addr:node_addr_t):
        self.distance_tbl = DistanceTbl(my_addr)
        self.pkts_received = 0
        self.received_data = list()
        self.pkts_dropped = 0
        self.last_dv = None
        self.tx_data = None


    def new_neighbor(self, addr:node_addr_t, link_cost:int):
        return self.distance_tbl.new_neighbor(addr, link_cost)


    def update(self, distance_vector:dict[node_addr_t, int], via:node_addr_t):
        return self.distance_tbl.update(distance_vector, via)


    def next_hop(self, dest:node_addr_t) -> node_addr_t|None:
        return self.distance_tbl.next_hop(dest)
    

    def get_distance_vector(self) -> dict[node_addr_t, int]:
        return self.distance_tbl.get_distance_vector()


class BellmanFordRouting(RoutingAlgorithm):
    def __init__(self):
        pass


    def determine_sender(self, cube:RoutingCube, rx_dir:Direction) -> node_addr_t:
        x, y, z = cube.position
        if rx_dir == Direction.UP:
            z += 1
        elif rx_dir == Direction.DOWN:
            z -= 1
        elif rx_dir == Direction.WEST:
            x -= 1
        elif rx_dir == Direction.EAST:
            x += 1
        elif rx_dir == Direction.NORTH:
            y += 1
        elif rx_dir == Direction.SOUTH:
            y -= 1
        return x, y, z
    

    def determine_tx_dir(self, cube:RoutingCube, neighbor:node_addr_t) -> Direction|None:
        src_x, src_y, src_z = cube.position
        dest_x, dest_y, dest_z = neighbor

        if dest_x == src_x + 1:
            dir = Direction.EAST
        elif dest_x == src_x - 1:
            dir = Direction.WEST
        elif dest_y == src_y + 1:
            dir = Direction.NORTH
        elif dest_y == src_y - 1:
            dir = Direction.SOUTH
        elif dest_z == src_z + 1:
            dir = Direction.UP
        elif dest_z == src_z - 1:
            dir = Direction.DOWN
        else:
            dir = None
            
        return dir
    

    def got_new_neighbor_notif(self, cube:RoutingCube, addr:node_addr_t, pkt:NewNeighborPkt):
        # Add neighbor to distance table
        cube.data.new_neighbor(addr, pkt.link_cost)
        if not pkt.ack:
            # If this is not an Ack, acknowledge the neighbor by sending the packet back
            pkt.ack = True
            cube.send_packet(self.determine_tx_dir(cube, addr), pkt)


    def send_new_neighbor_notif(self, cube:RoutingCube):
        # Create new neighbor notification packet
        nn_pkt = NewNeighborPkt()
        # Notify all neighbors
        for d in list(Direction):
            cube.send_packet(d, nn_pkt)


    def update_distance_tbl(self, cube:RoutingCube, distance_vector:dict[node_addr_t, int], via:node_addr_t):
        # Update internal distance table with a distance vector from a neighbor node
        cube.data.update(distance_vector, via)


    def update_neighbors(self, cube:RoutingCube):
        # Create distance vector packet
        dv_pkt = DistanceVectorPkt(cube.data.get_distance_vector())

        # Only update neighbors if distance table has not converged
        if cube.data.last_dv != dv_pkt.vector:
            for d in list(Direction):
                cube.send_packet(d, dv_pkt)
            cube.data.last_dv = dv_pkt.vector

    
    def generate_pkt(self, cube:RoutingCube, data:int, dest_addr:node_addr_t):
        cube.data.tx_data = DataPkt(dest_addr, data)


    def route_pkt(self, cube:RoutingCube, pkt:DataPkt):
        if pkt.dest == cube.position:
            # This cube is the destination
            cube.data.pkts_received += 1
            cube.data.received_data.append(pkt)
        else:
            # Route the packet toward the destination using Bellman Ford
            next_hop = cube.data.next_hop(pkt.dest)
            if next_hop is None:
                # This cube does not know a route to the destination
                cube.data.pkts_dropped += 1
                return
            # Send the packet in the appropriate direction
            tx_dir = self.determine_tx_dir(cube, next_hop)
            cube.send_packet(tx_dir, pkt)


    def route(self, cube:RoutingCube):
        # Get a packet received by the cube
        pkt, rx_dir = cube.get_packet()
        if pkt is not None:
            # Determine the address of the packet sender based on the face it came from
            tx_addr = self.determine_sender(cube, rx_dir)

            if isinstance(pkt, NewNeighborPkt):
                # Cube got notified of new neighbor node - add the neighbor and send distance vector
                self.got_new_neighbor_notif(cube, tx_addr, pkt)
                self.update_neighbors(cube)
            
            elif isinstance(pkt, DistanceVectorPkt):
                # Cube received distance vector from node - update table and send distance vector
                self.update_distance_tbl(cube, pkt.vector, tx_addr)
                self.update_neighbors(cube)

            elif isinstance(pkt, DataPkt):
                # Cube received data packet with a destination address
                self.route_pkt(cube, pkt)

            else:
                raise TypeError(f"Bad packet type: {type(pkt)}")
            
        # Transmit a packet generated by this cube if one exists
        if cube.data.tx_data is not None:
            self.route_pkt(cube, cube.data.tx_data)
            cube.data.tx_data = None
        
        return cube


    def power_on(self, cube:RoutingCube):
        # Initialize cube data and notify neighbor nodes of the cube's existence
        cube.data = BellmanFordData(cube.position)
        self.send_new_neighbor_notif(cube)

    
    def send_packet(self, cube:RoutingCube, dest_addr:node_addr_t, data:typing.Any):
        # Generate data packet with the destination address in this cube
        cube.data.tx_data = DataPkt(dest_addr, data)


class BellmanFordRobot(RobotAlgorithm):
    def __init__(self) -> None:
        self.internal_cube_algo = BellmanFordRouting()


    def step(self, robot: Robot) -> RoutingCube:
        self.internal_cube_algo.route(robot.cube)
        

    def power_on(self, robot: Robot) -> None:
        self.internal_cube_algo.power_on(robot.cube)
