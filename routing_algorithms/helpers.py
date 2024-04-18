"""Helper Functions for Routing Algorithms

file: helpers.py
author: Mark Danza
"""

import typing

from network.faces import Direction

node_addr_t: typing.TypeAlias = int|str
node_pos_t: typing.TypeAlias = tuple[int|int|int]


def determine_tx_pos(my_pos:node_pos_t, rx_dir:Direction) -> node_pos_t:
    """
    Helper function for determining the position of a neighbor node that sent a packet
    from the specified direction.

    :param my_pos: position of reference node
    :param rx_dir: direction data was received from
    :return: address of neighbor node
    """
    x, y, z = my_pos
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


def determine_tx_dir(my_pos:node_pos_t, neighbor_pos:node_pos_t) -> Direction|None:
    """
    Helper function for determining the appropriate direction of transmission (out of a
    cube) for sending data to the specified neighbor node.

    :param my_pos: position of reference node
    :param neighbor_pos: position of neighbor node
    :return: direction of neighbor, or None if the specified neighbor is not actually
    adjacent to the reference node
    """
    src_x, src_y, src_z = my_pos
    dest_x, dest_y, dest_z = neighbor_pos

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
