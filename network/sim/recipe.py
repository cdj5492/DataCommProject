"""
file: recipe.py
author: Mark Danza
"""

import enum
import io
import os
import typing

from network.network_grid import NetworkGrid
from network.faces import Direction


class RecipeComm(enum.Enum):
    """
    Defines the valid commands for simulation recipes.
    """
    ADDN = enum.auto()
    ADDR = enum.auto()
    RMVN = enum.auto()
    SEND = enum.auto()
    WAIT = enum.auto()
    LOOP = enum.auto()
    ENDL = enum.auto()


    @classmethod
    def get_valid_commands(cls) -> list[str]:
        return [item.name for item in cls]
    

    @classmethod
    def expected_arg_nums(cls) -> dict:
        return {
            cls.ADDN : 3,
            cls.ADDR : 3,
            cls.RMVN : 3,
            cls.SEND : 5,
            cls.WAIT : 1,
            cls.LOOP : 1,
            cls.ENDL : 0,
        }
    

    def num_args_expected(self) -> int:
        arg_nums = RecipeComm.expected_arg_nums()
        try:
            return arg_nums[self]
        except KeyError:
            raise NotImplementedError(f"Expected argument number not implemented for recipe command '{self}'")


class Recipe:
    def __init__(self, commands:typing.Iterable[RecipeComm], command_args:typing.Iterable[typing.Iterable]):
        if len(commands) != len(command_args):
            raise ValueError("Number of recipe commands must equal number of argument sets")
        
        self.commands = list(commands)
        self.command_args = list(command_args)

        self.idx = 0
        self.length = len(self.commands)

        self.wait_cycles_remaining = 0

        self.loop_iters_remaining = 0
        self.loop_idx = 0
        self.in_loop = False


    @classmethod
    def from_file(cls, f:os.PathLike, check_arg_count:bool=True):
        commands = list()
        command_args = list()

        with open(f) as fd:
            data = fd.readlines()

        for linenum, line in enumerate(data, start=1):
            # Skip empty lines
            line = line.strip()
            if len(line) == 0:
                continue
        
            # Split line on space delimiter
            items = line.split(' ')

            # Skip commented lines
            if items[0] == '#':
                continue

            # Get command and arguments from line items
            comm = items[0]
            args = items[1:]

            # Convert command to RecipeComm
            try:
                comm = RecipeComm[comm]
            except KeyError:
                e = ValueError(f"Invalid recipe file: invalid command '{comm}'")
                e.add_note(f"(line {linenum} in {f})")
                raise e

            # Convert arguments to int
            try:
                args = [int(arg) for arg in args]
            except ValueError:
                e = ValueError(f"Invalid recipe file: all arguments must be integers")
                e.add_note(f"(line {linenum} in {f})")
                raise e
            
            # Check argument count
            if check_arg_count:
                try:
                    cls._check_arg_count(comm, args)
                except ValueError as e:
                    e.add_note(f"(line {linenum} in {f})")
                    raise e

            commands.append(comm)
            command_args.append(args)

        return cls(commands, command_args)
    

    @staticmethod
    def _check_arg_count(comm:RecipeComm, args:typing.Iterable):
        if comm.num_args_expected() != len(args):
            raise ValueError(
                f"Invalid number of arguments for recipe command '{comm.name}': expected {comm.num_args_expected()}, got {len(args)}"
            )


    def handle_ADDN(self, netgrid:NetworkGrid, x:int, y:int, z:int):
        netgrid.add_node(x, y, z)


    def handle_ADDR(self, netgrid:NetworkGrid, x:int, y:int, z:int):
        netgrid.add_robot(x, y, z)


    def handle_RMVN(self, netgrid:NetworkGrid, x:int, y:int, z:int):
        netgrid.remove_node(x, y, z)


    def handle_SEND(self, netgrid:NetworkGrid, data:typing.Any, src_x:int, src_y:int, src_z:int, dir:int):
        # TODO accept dst_x, dst_y, dst_z instead of dir
        # NetworkGrid should probably have a send_packet(data, src, dst) method
        node = netgrid.get_node(src_x, src_y, src_z)
        node.send_packet(Direction(dir), data)


    def handle_WAIT(self, netgrid:NetworkGrid, cycles:int):
        self.wait_cycles_remaining = cycles


    def handle_LOOP(self, netgrid:NetworkGrid, iterations:int):
        if self.in_loop:
            raise RuntimeError("Nested loops in recipes not allowed")

        self.loop_idx = self.idx
        self.loop_iters_remaining = iterations
        self.in_loop = True


    def handle_ENDL(self, netgrid:NetworkGrid):
        if not self.in_loop:
            raise RuntimeError("Cannot end loop in recipe - no loop was started")
        
        if self.loop_iters_remaining == 0:
            self.in_loop = False
        else:
            self.loop_iters_remaining -= 1
            self.idx = self.loop_idx


    def handle_comm(self, netgrid:NetworkGrid, comm:RecipeComm, args:typing.Iterable):
        Recipe._check_arg_count(comm, args)

        if comm == RecipeComm.ADDN:
            self.handle_ADDN(netgrid, *args)
        elif comm == RecipeComm.ADDR:
            self.handle_ADDR(netgrid, *args)
        elif comm == RecipeComm.RMVN:
            self.handle_RMVN(netgrid, *args)
        elif comm == RecipeComm.SEND:
            self.handle_SEND(netgrid, *args)
        elif comm == RecipeComm.WAIT:
            self.handle_WAIT(netgrid, *args)
        elif comm == RecipeComm.LOOP:
            self.handle_LOOP(netgrid, *args)
        elif comm == RecipeComm.ENDL:
            self.handle_ENDL(netgrid, *args)
        else:
            raise ValueError(f"Unsupported recipe command: '{comm}'")


    def execute_next(self, netgrid:NetworkGrid):
        if self.is_running():
            # Do not execute next command if waiting
            if self.wait_cycles_remaining > 0:
                self.wait_cycles_remaining -= 1
                return

            comm = self.commands[self.idx]
            args = self.command_args[self.idx]
            self.handle_comm(netgrid, comm, args)
            self.idx += 1


    def is_running(self) -> bool:
        return self.length > self.idx


    def __str__(self) -> str:
        with io.StringIO() as sio:
            sio.write("Recipe:")
            for comm, args in zip(self.commands, self.command_args):
                sio.write(f"\n  {comm.name}")
                for arg in args:
                    sio.write(" " + str(arg))
            return sio.getvalue()
