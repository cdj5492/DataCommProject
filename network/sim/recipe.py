"""Recipe Framework for Specifying Simulation Instructions

file: recipe.py
author: Mark Danza

Recipe File Formatting:
 - One command per line.
 - Each line contains a command name followed by integer arguments, space-delimited.
 - Command arguments may only be integers.
 - Blank lines and commented lines (starting with '#') are ignored.

How Recipes Work:
 - One command is executed every cycle, unless there is a WAIT.
 - A WAIT command causes the recipe execution to be effectively paused for several
   cycles. This can be used to allow things to happen in the network simulation before
   continuing with the recipe.
 - The LOOP and ENDL commands can be used to execute the enclosed block of commands
   multiple times.
 - To make an infinite loop, pass a negative value as the argument for LOOP.
 - Nested loops are not allowed.

The following commands are allowed in recipe files:
 - ADDN x y z: Add a node to the network at the specified coordinates.
 - ADDR x y z: Add a robot node to the network at the specified coordinates.
 - RMVN x y z: Removes the node at the specified coordinates from the network. May also
   be used to remove robot nodes.
 - SEND data src_x src_y src_z direction: Sends the given data from the node specified by
   the src coordinates out of the face specified by the direction.
 - WAIT n: The recipe will do nothing for n+1 cycles.
 - LOOP n: The recipe will execute the enclosed block of commands for n+1 iterations.
 - ENDL: Denotes the end of a loop block.
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
        """
        Returns a list of the valid commands strings that can be in a recipe file.

        :return: valid command strings
        """
        return [item.name for item in cls]
    

    @classmethod
    def expected_arg_counts(cls) -> dict:
        """
        Generates a dictionary of the expected argument counts for each valid command.

        :return: RecipeComm : int dictionary
        """
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
        """
        Gets the number of arguments expected for this type of command.

        :raises NotImplementedError: if there is no entry for this command in the
        dictionary returned by expected_arg_counts() (for development purposes)
        :return: expected argument count of this command
        """
        arg_nums = RecipeComm.expected_arg_counts()
        try:
            return arg_nums[self]
        except KeyError:
            raise NotImplementedError(f"Expected argument number not implemented for recipe command '{self}'")


class Recipe:
    """
    Class that represents and executes a set of instructions for network simulation using
    a NetworkGrid.
    """

    def __init__(self, commands:typing.Iterable[RecipeComm], command_args:typing.Iterable[typing.Iterable]):
        """
        Initialize a recipe with the given steps.

        :param commands: ordered collection of commands
        :param command_args: ordered collection of command argument sets corresponding to
                             the given commands
        :raises ValueError: if commands and command_args have different lengths
        """
        if len(commands) != len(command_args):
            raise ValueError("Number of recipe commands must equal number of argument sets")
        
        self.commands = list(commands)         # Sequence of commands
        self.command_args = list(command_args) # Argument sets corresponding to the commands

        self.idx = 0                           # Index of the next command to execute
        self.length = len(self.commands)       # Total number of individual commands

        self.wait_cycles_remaining = 0         # Number of cycles remaining after a wait command

        self.loop_iters_remaining = 0          # Number of iterations remaining after a loop command
        self.loop_idx = 0                      # Index to return to at the end of a loop body
        self.in_loop = False                   # Whether the recipe is currently executing a loop body


    @classmethod
    def from_file(cls, f:os.PathLike, check_arg_count:bool=True):
        """
        Initializes a recipe from the given file.

        :param f: recipe file (.txt)
        :param check_arg_count: whether to validate the number of arguments given for
                                each command
        :raises ValueError: if the recipe file is formatted improperly
        :return: recipe containing the instructions loaded from the file
        """
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
        """
        Helper method for validating the argument count and raising the appropriate
        exception if it is incorrect.

        :param comm: command type
        :param args: arguments specified for the given command
        :raises ValueError: if the length of args is not equal to the number of expected
        arguments for comm
        """
        if comm.num_args_expected() != len(args):
            raise ValueError(
                f"Invalid number of arguments for recipe command '{comm.name}': expected {comm.num_args_expected()}, got {len(args)}"
            )


    def handle_ADDN(self, netgrid:NetworkGrid, x:int, y:int, z:int):
        """
        Handling method for ADDN commands.

        Adds a node at the specified coordinates.

        :param netgrid: network grid to operate on
        :param x: x-coordinate
        :param y: y-coordinate
        :param z: z-coordinate
        """
        netgrid.add_node(x, y, z)


    def handle_ADDR(self, netgrid:NetworkGrid, x:int, y:int, z:int):
        """
        Handling method for ADDR commands.

        Adds a robot node at the specified coordinates.

        :param netgrid: network grid to operate on
        :param x: x-coordinate
        :param y: y-coordinate
        :param z: z-coordinate
        """
        netgrid.add_robot(x, y, z)


    def handle_RMVN(self, netgrid:NetworkGrid, x:int, y:int, z:int):
        """
        Handling method for RMVN commands.

        Removes a node from the specified coordinates.

        :param netgrid: network grid to operate on
        :param x: x-coordinate
        :param y: y-coordinate
        :param z: z-coordinate
        """
        netgrid.remove_node(x, y, z)


    def handle_SEND(self, netgrid:NetworkGrid, data:typing.Any, src_x:int, src_y:int, src_z:int, dir:int):
        """
        Handling method for SEND commands.

        Sends the given data from the source node to the adjacent node in the specified
        direction.

        :param netgrid: network grid to operate on
        :param data: data to send
        :param src_x: x-coordinate of source node
        :param src_y: y-coordinate of source node
        :param src_z: z-coordinate of source node
        :param dir: face direction to send the data on
        """
        # TODO accept dst_x, dst_y, dst_z instead of dir
        # NetworkGrid should probably have a send_packet(data, src, dst) method
        node = netgrid.get_node(src_x, src_y, src_z)
        node.send_packet(Direction(dir), data)


    def handle_WAIT(self, netgrid:NetworkGrid, cycles:int):
        """
        Handling method for WAIT commands.

        Causes the recipe to do nothing for the next several calls to execute_next(),
        where cycles is the number of subsequent calls that will be spent waiting.
        Including the call that handles the WAIT command, the recipe will do nothing for
        a total of cycles + 1 calls.

        :param netgrid: unused
        :param cycles: number of additional cycles to wait for
        """
        self.wait_cycles_remaining = cycles


    def handle_LOOP(self, netgrid:NetworkGrid, iterations:int):
        """
        Handling method for LOOP commands.

        Indicates that the recipe is entering a loop. The loop will be executed a total
        of iterations + 1 times.

        :param netgrid: unused
        :param iterations: number of iterations in the loop (use a negative value for an
                           infinite loop)
        :raises RuntimeError: if the recipe is already in a loop when this method is
        called
        """
        if self.in_loop:
            raise RuntimeError("Nested loops in recipes not allowed")

        self.loop_idx = self.idx
        self.loop_iters_remaining = iterations
        self.in_loop = True


    def handle_ENDL(self, netgrid:NetworkGrid):
        """
        Handling method for ENDL commands.

        Indicates that the recipe has reached the end of a loop body. If there are
        iterations remaining in the loop, the recipe's index will be set to the index of
        the LOOP command that started the loop. (Note that the recipe index is
        incremented after each command is handled, preventing the LOOP command from being
        executed again.)

        :param netgrid: unused
        :raises RuntimeError: if the recipe is not in a loop when this method is called
        """
        if not self.in_loop:
            raise RuntimeError("Cannot end loop in recipe - no loop was started")
        
        if self.loop_iters_remaining == 0:
            self.in_loop = False
        else:
            self.loop_iters_remaining -= 1
            self.idx = self.loop_idx


    def handle_comm(self, netgrid:NetworkGrid, comm:RecipeComm, args:typing.Iterable):
        """
        Calls the appropriate handling method for the given command.

        :param netgrid: network grid to operate on
        :param comm: command
        :param args: command arguments
        :raises ValueError: if args does not contain the expected number of arguments for
        the given command or if the given command is invalid
        """
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
        """
        Executes the next instruction in the recipe (the instruction currently pointed to
        by the recipe's internal index), or does nothing if the recipe is in a waiting
        state. Calling this method is analogous to "stepping" the network grid (but this
        mehod does not call NetworkGrid.step()).

        :param netgrid: network grid to operate on
        """
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
        """
        Helper method for determining whether this recipe is currently running. A recipe
        is running if it has not reached its end.

        :return: True if the recipe is running
        """
        return self.length > self.idx


    def __str__(self) -> str:
        with io.StringIO() as sio:
            sio.write("Recipe:")
            for comm, args in zip(self.commands, self.command_args):
                sio.write(f"\n  {comm.name}")
                for arg in args:
                    sio.write(" " + str(arg))
            return sio.getvalue()