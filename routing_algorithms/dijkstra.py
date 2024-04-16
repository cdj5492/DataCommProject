import dataclasses
import typing

from network.robot import Robot
from network.routing_cube import RoutingCube
from network.faces import Direction
from robot_algorithm.robot_algorithm import RobotAlgorithm
from routing_algorithms.helpers import node_addr_t, determine_tx_dir, determine_tx_addr
from routing_algorithms.routing_algorithm import RoutingAlgorithm

BMF_DEFAULT_LINK_COST = 1


import heapq
import sys

# Class representing a node in the graph
class Node:
    def __init__(self, name):
        self.name = name
        self.adjacent = {}
        self.distance = sys.maxsize
        self.visited = False
        self.previous = None

    def add_neighbor(self, neighbor, weight):
        self.adjacent[neighbor] = weight

# Dijkstra algorithm function
def dijkstra(start_node):
    start_node.distance = 0
    # Use a priority queue to keep track of the next node to visit
    priority_queue = [(node.distance, node) for node in graph.values()]
    heapq.heapify(priority_queue)

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_distance > current_node.distance:
            continue

        for neighbor, weight in current_node.adjacent.items():
            distance = current_node.distance + weight
            if distance < neighbor.distance:
                neighbor.distance = distance
                neighbor.previous = current_node
                heapq.heappush(priority_queue, (distance, neighbor))

# Function to get shortest path
def get_shortest_path(target_node):
    path = []
    current_node = target_node
    while current_node:
        path.insert(0, current_node.name)
        current_node = current_node.previous
    return path

# Sample graph
graph = {
    'A': Node('A'),
    'B': Node('B'),
    'C': Node('C'),
    'D': Node('D'),
    'E': Node('E'),
}

graph['A'].add_neighbor(graph['B'], 4)
graph['A'].add_neighbor(graph['C'], 2)
graph['B'].add_neighbor(graph['D'], 5)
graph['C'].add_neighbor(graph['B'], 1)
graph['C'].add_neighbor(graph['D'], 8)
graph['D'].add_neighbor(graph['E'], 3)

# Execute Dijkstra algorithm
start_node = graph['A']
dijkstra(start_node)

# Get shortest path to node E
target_node = graph['E']
shortest_path = get_shortest_path(target_node)
print("Shortest path to node E:", shortest_path)
