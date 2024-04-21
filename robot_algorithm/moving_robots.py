"""
"""

import dataclasses

from network.robot import Robot
from network.routing_cube import RoutingCube
from robot_algorithm.robot_algorithm import RobotAlgorithm
from routing_algorithms.helpers import node_addr_t

NUM_CYCLES_BETWEEN_MOVES = 20
NUM_CYCLES_TO_MOVE = 10


@dataclasses.dataclass
class MovingRobotData:
    cycles_till_next_move: int = NUM_CYCLES_BETWEEN_MOVES
    cycles_till_done_moving: int = 0


class MovingRobotAlgorithm(RobotAlgorithm):
    def __init__(self):
        self.robots_in_transit = dict()
    

    @staticmethod
    def robot_cycles_till_next_move(robot:Robot) -> int:
        return robot.cube.data.cycles_till_next_move
    

    @staticmethod
    def robot_cycles_till_done_moving(robot:Robot) -> int:
        return robot.cube.data.cycles_till_done_moving
    

    def robot_start_move(self, robot:Robot):
        robot.cube.data.robot_cycles_till_done_moving = NUM_CYCLES_TO_MOVE

        # TODO robot algorhtm or needs a way to remove a robot from the netgrid
        # Or robot needs a way to remove itself from the netgrid

        self.robots_in_transit[robot.cube.id] = robot


    def robot_end_move(self, robot_id:node_addr_t):
        pass


    def step(self, robot:Robot) -> RoutingCube:
        cycles_left = self.robot_cycles_till_next_move(robot)
        if cycles_left <= 0:
            self.robot_start_move(robot)
        else:
            robot.cube.data.cycles_till_next_move -= 1    


    def power_on(self, robot:Robot):
        robot.cube.data = MovingRobotData()
