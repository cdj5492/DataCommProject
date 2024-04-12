"""Helper Functions for Routing Algorithms

file: helpers.py
author: Mark Danza
"""

import typing

from network.faces import Direction

node_addr_t: typing.TypeAlias = tuple[int,int,int]


def determine_tx_addr(my_addr:node_addr_t, rx_dir:Direction) -> node_addr_t:
    """
    Helper function for determining the address of a neighbor node that sent a packet
    from the specified direction.

    :param my_addr: address of reference node
    :param rx_dir: direction data was received from
    :return: address of neighbor node
    """
    x, y, z = my_addr
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


def determine_tx_dir(my_addr:node_addr_t, neighbor_addr:node_addr_t) -> Direction|None:
    """
    Helper function for determining the appropriate direction of transmission (out of a
    cube) for sending data to the specified neighbor node.

    :param my_addr: address of reference node
    :param neighbor_addr: address of neighbor node
    :return: direction of neighbor, or None if the specified neighbor is not actually
    adjacent to the reference node
    """
    src_x, src_y, src_z = my_addr
    dest_x, dest_y, dest_z = neighbor_addr

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
