"""Spanning Tree Algorithm

file: spanningtree.py
author: Shams Faruque

"""

import dataclasses
import math
import typing
import sys

from network.robot import Robot
from network.routing_cube import RoutingCube
from network.faces import Direction
from robot_algorithm.robot_algorithm import RobotAlgorithm
from routing_algorithms.helpers import node_addr_t, node_pos_t, determine_tx_dir, determine_tx_pos
from routing_algorithms.routing_algorithm import RoutingAlgorithm
import copy


BMF_DEFAULT_LINK_COST = 1
BMF_INFINITE_LINK_COST = math.inf


@dataclasses.dataclass
class MSTPkt:
    """
    Destination PKT:
        src_addr : Holds the source addr
        dest_addr : Holds the destination addr
    """
    src_addr : node_addr_t
    dest_addr : node_addr_t|None


@dataclasses.dataclass
class MSTInitPKT():
    """
    Initialzation Packet:
        list : Holds all nodes that have been transversed
        send_to_root : Knows when it has to go back to root 
        curr_level : The root level relative to root (0 : root, 1 : 1 level away, 2 : 2 levels away ...)
    """
    list : typing.List = dataclasses.field(default_factory=list)
    send_to_root : bool = False
    curr_level : int = 0

    def copy(self):
        return MSTInitPKT(
            list=self.list.copy(),
            send_to_root=self.send_to_root,
            curr_level=self.curr_level
        )
    
@dataclasses.dataclass
class MSTBroadcast(MSTInitPKT):

    def copy(self):
        return copy.copy(self)   


@dataclasses.dataclass
class MSTDataPkt(MSTPkt):
    """
    Generic packet type with a data payload.
    """
    payload: typing.Any

    def copy(self):
        return copy.copy(self)

class SpannningTreeData:
    """

    This class should be used for RoutingCube.data.
    """

    def __init__(self, my_addr:node_addr_t, my_pos:node_pos_t):
        """
        Create new Spanning Tree data with an empty distance table.

        :param my_addr: address of the node that owns this data
        :param my_pos:  the position in (x,y,z)
        """

        self.isVisited = False       # True if routing algorthim is intialized 
        self.dir = dict()            # Direction towards root
        self.my_addr = my_addr       # Name (ID)
        self.my_pos = my_pos         # (x,y,z) position
        self.curr_level = 0          # Node level relative to root
        self.num_path = 0            # Number of path
        self.tx_data = None          # MSTDataPkt to send from this node
        self.broadcast_count = 30 
 

    def new_neighbor(self, addr:node_addr_t, pos:node_pos_t, link_cost:int):
        pass
    

    def lost_neighbor(self, addr:node_addr_t):
        pass 


    def update(self, distance_vector:dict[node_addr_t, int], via:node_addr_t, via_pos:node_pos_t):
        pass


    def next_hop(self, dest:node_addr_t) -> node_pos_t|None:
        pass
    

    def get_distance_vector(self) -> dict[node_addr_t, int]:
        pass


class SpanningTreeRouting(RoutingAlgorithm):
    """
    Routing algorithm class for Spanning Tree Routing
    """
    
    
    def __init__(self):
        self.root_id = None
        self.got_packet = 0


    def route_pkt(self, cube:RoutingCube, pkt:MSTDataPkt):
        pass


    def route(self, cube:RoutingCube):


        if(cube.id == self.root_id):
            cube.data.broadcast_count += 1

        # Get a packet received by the cube
        pkt, rx_dir = cube.get_packet()

        '''
        Intialization phase
        '''

        '''
        Starts the initialization sending out the intialization packet.
        '''

        # Step 1: Generate init packet from root
        if (cube.id == self.root_id and cube.data.isVisited == False):
            
            # Step 1.6: Set visited to true
            cube.data.isVisited = True

            # Step 1.1 : Generate packet init packet
            init_packet = MSTInitPKT()

            # Step 1.2 : Set the current level
            cube.data.curr_level = init_packet.curr_level

            # Step : Adding cube_id to list
            init_packet.list.append(cube.id)

            # Step 1.3: Add root to dict 
            #init_packet.dict[cube.data.curr_level] = [cube.id, "Root"]

            # Step 1.4 : Increment the current level
            init_packet.curr_level +=1

            # Step 1.5 : Send init packet to neighbors 
            for d in list(Direction):
                if(cube.connected_in_direction(d) is True):
                    cube.send_packet(d, init_packet.copy())

        if(cube.id == self.root_id and cube.data.broadcast_count == 30):
            brod_pkt = MSTBroadcast()
            cube.data.isVisited == False
            if(cube.connected_in_direction(d) is True):
                cube.send_packet(d, brod_pkt.copy())   

        '''
        When there is a packet in the system.
            Init_packet 
            Data_packet
        '''

        # Step 2 : Check is there is a packet
        if pkt is not None:

            # Step 2.1 : Check if the packet is a init packet
            if isinstance(pkt, MSTInitPKT):

                #  Step 2.1.1 : Node was not visited by the init_packet
                if cube.data.isVisited == False:
                    # Step 2.1.1.5 : Check if there are any neighbors
                    cube.data.isVisited = True 

                    # Step 2.1.1.1 : Set the current level
                    cube.data.curr_level = pkt.curr_level

                    # Step 2.1.1.2: Set the direction to root node
                    cube.data.dir[cube.data.num_path] = [self.root_id,rx_dir]

                    # Step 2.1.2.1.2.4 : Increment path
                    cube.data.num_path += 1

                    # Step : Adding cube_id to list
                    pkt.list.append(cube.id)

                    # Step 2.1.1.4 : Check if there are any neighbors
                    isNeighbors = False

                    dir_list = []

                    pkt2, rx_dir2 = cube.get_packet()


                    while(pkt2!=None):
                        if(pkt2.curr_level >= cube.data.curr_level):
                            dir_list.append(rx_dir2)
                        pkt2, rx_dir2 = cube.get_packet()

                    for d in list(Direction):
                        
                        if(d is not rx_dir and not (d in dir_list)):
                            isNeighbors |= cube.connected_in_direction(d)

                    # Step 2.1.1.5 : If no neigbors set the packet to be returned to root
                    if isNeighbors is False:
                                         
                        # Step 2.1.1.6.1 : Sets the init packet to be sent back
                        pkt.send_to_root = True

                        # Step 2.1.1.6.2 : Decrement the level
                        pkt.curr_level -= 1

                        # Step 2.1.1.6.3 : Sends the packet back
                        _ = cube.send_packet(cube.data.dir[0][1], pkt.copy())
                    
                    # Step 2.1.1.6 : There are neighbors so send the packet
                    else :
                        # Step 2.1.1.3: Incremnet the level
                        pkt.curr_level +=1

                        # Step 2.1.7.1 : Send the neighbor the packet 
                        for d in list(Direction):
                             if(cube.connected_in_direction(d) is True and d is not rx_dir):
                                cube.send_packet(d, pkt.copy())
                        
                # Step 2.1.2 : Node was already visited                   
                else :
                    
                    # Step 2.1.2.1: Node was already visited and packet is being sent back 
                    if(pkt.send_to_root == True):

                        # Step 2.1.2.1.1: Check if the intialization pkt is at the root 
                        if (cube.id == self.root_id):

                            # Step 2.1.2.1.1.1 : Append direction element to list
                            cube.data.dir[cube.data.num_path] = [pkt.list, rx_dir]

                            # Step 2.1.2.1.1.2 : Increment path
                            cube.data.num_path += 1                        
                        # Step 2.1.2.1.2: Check if the intialization pkt is not at the root and its the right path 
                        else:

                            # Step 2.1.2.1.2.1 : Append direction element to list
                            cube.data.dir[cube.data.num_path] = [pkt.list[(pkt.list.index(cube.id)+1):], rx_dir]

                            # Step 2.1.2.1.2.2 : Send the packet 
                            _= cube.send_packet(cube.data.dir[0][1], pkt)

                            # Step 2.1.2.1.2.3 : Decrement level
                            pkt.curr_level -= 1

                             # Step 2.1.2.1.2.4 : Increment path
                            cube.data.num_path += 1

            elif isinstance(pkt, MSTDataPkt):
                if pkt.dest_addr == cube.id:
                    cube.notify_correctly_routed_pkt()
                else:        
                    to_root = True
                    path_index = 0
                   
                    for i in range(len(cube.data.dir) - 1, 0, -1):
                        for j in range(len(cube.data.dir[i][0])):
                            if cube.data.dir[i][0][j] == pkt.dest_addr:
                                to_root = False
                                path_index = i
                    if to_root:
                        cube.send_packet(cube.data.dir[0][1], pkt) 
                    else:
                        cube.send_packet(cube.data.dir[path_index][1], pkt)    

            elif isinstance(pkt, MSTBroadcast):
                cube.data.isVisited = False
                for d in list(Direction):
                    if(cube.connected_in_direction(d) is True and d is not rx_dir):
                            cube.send_packet(MSTBroadcast, pkt.copy())


    def power_on(self, cube:RoutingCube):
        """
        Initialize the cube's routing data and send new neighbor notifications to its
        neighbors.

        :param cube: RoutingCube to operate on
        """
        cube.data = SpannningTreeData(cube.id, cube.position)

        if(self.root_id == None):
            self.root_id = cube.id

        
    

    
    def send_packet(self, cube:RoutingCube, dest_addr:node_addr_t, data:typing.Any):
        """
        Method used to trigger a packet transmission from this cube to the destination
        node, which will be handled by the routing algorithm.

        :param cube: RoutingCube to operate on
        :param dest_addr: destination node address
        :param data: packet payload
        """
        # Generate data packet with the destination address in this cube
        for d in list(Direction):
            if(cube.connected_in_direction(d) is True):
                cube.send_packet(d,(MSTDataPkt(cube.id, dest_addr, data)).copy())
                break

class SpanningTreeRobot(RobotAlgorithm):
    """
    
    """

    CUBE_ROUTING_ALGO = SpanningTreeRouting()

    def __init__(self):
        pass


    def step(self, robot: Robot) -> RoutingCube:
        #SpanningTreeRobot.CUBE_ROUTING_ALGO.power_on(robot.cube)
        pass

    def power_on(self, robot: Robot):
        #SpanningTreeRobot.CUBE_ROUTING_ALGO.power_on(robot.cube)
        pass

