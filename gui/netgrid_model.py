"""Model Class for NetworkGrid Simulator

file: netgrid_model.py
author: Mark Danza

This contains a class which encapsulates a NetworkGrid object with the functions required
for any network simulator Model.
"""

import typing

import numpy as np

from gui.color_conf import NODE_COLOR_CONFS, VALID_COLOR_CONFS
from gui.utils import VoxelData, Model, ColorConf, ColorConfGroup
from network.network_grid import NetworkGrid
from network.robot import Robot
from network.routing_cube import NodeDiagnostics, RoutingCube
from network.sim.recipe import Recipe


class RoutingCubeVoxelData(VoxelData):
    """
    Requires that any color configurations used have the function signature given by
    COLOR_CONF_EVAL_FUNC.
    """
    
    COLOR_CONF_EVAL_FUNC: typing.TypeAlias = typing.Callable[[NodeDiagnostics], typing.Any]


    def __init__(self, cube:RoutingCube, color_conf:ColorConf|ColorConfGroup):
        super().__init__(cube.position)
        self.diagnostics = cube.stats
        self.color_conf = color_conf
    

    def facecolor(self) -> tuple[float,float,float,float]:
        colors = self.color_conf(self.diagnostics)
        return colors.vals()


class NetGridPresenter(Model):
    """
    "Presenter" class that acts as an intermediary between the NetworkGrid backend and
    the user interface.
    """

    def __init__(self, netgrid:NetworkGrid, dimensions:tuple[int,int,int], recipe:Recipe|None=None):
        """
        Creates a presenter for the given grid.

        :param netgrid: simulator backend
        :param dimensions: (x,y,z) dimensions of grid to plot the network in
        """
        self.netgrid = netgrid
        self.dimensions = dimensions
        self.recipe = recipe
        super().__init__()


    def get_network_dimensions(self) -> tuple[int, int, int]:
        return self.dimensions


    def get_node_voxeldata(self, mode:str) -> list[RoutingCubeVoxelData]:
        if mode not in VALID_COLOR_CONFS:
            raise ValueError(f"Invalid node color configuration '{mode}'")

        nodes = self.netgrid.node_list
        color_conf = NODE_COLOR_CONFS[mode]

        return [RoutingCubeVoxelData(node, color_conf) for node in nodes] 


    def next_state(self):
        """
        Step the internal NetworkGrid and recipe, if applicable. If a recipe exists, it
        is stepped first.
        """
        # Execute next recipe cycle
        if self.recipe is not None:
            # Resume recipe if paused
            self.recipe.resume()
            self.recipe.execute_next(self.netgrid)
        # Step network grid and update observers
        self.netgrid.step()
        self.alert_observers()


    def restart(self):
        # TODO Currently no way to reset to initial state
        pass


    def run(self, num_cycles:int=-1, ignore_pauses:bool=False):
        """
        Repeatedly steps to the next state until the internal recipe is finished running
        or becomes paused. Alternatively, a specific number of recipe cycles can be run.
        Does nothing if there is no recipe.

        WARNING: This function may block forever if the recipe has an infinite loop with
        no pauses and num_cycles < 0.

        :param num_cycles: maximum number of cycles to run; may be negative to run with
                           no maximum
        :param ignore_pauses: set this to skip over pause commands while running
        """
        if self.recipe is not None:
            # Resume recipe if paused
            self.recipe.resume()

            # Execute recipe instruction and step network grid each cycle
            while self.recipe.is_running() and num_cycles != 0:
                self.recipe.execute_next(self.netgrid)
                self.netgrid.step()

                # Automatically resume a paused recipe if pauses are ignored
                if ignore_pauses:
                    self.recipe.resume()

                # Decrement the number of cycles (will never cause the loop to exit if num_cycles < 0)    
                num_cycles -= 1            

            # Update observers with resulting end state
            self.alert_observers()
