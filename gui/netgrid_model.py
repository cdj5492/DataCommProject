"""Model Class for NetworkGrid Simulator

file: netgrid_model.py
author: Mark Danza

This contains a class which encapsulates a NetworkGrid object with the functions required
for any network simulator Model.
"""

import typing

from app.support import NODE_COLOR_CONFS, VALID_COLOR_CONFS
from gui.utils import NodeUIData, Model, ColorConf, ColorConfGroup
from network.network_grid import NetworkGrid
from network.routing_cube import NodeDiagnostics, RoutingCube
from network.recipe import Recipe


class RoutingCubeUIData(NodeUIData):
    """
    Node UI data type for extracting GUI data from RoutingCube objects.

    Requires that any color configurations used have the function signature given by
    COLOR_CONF_EVAL_FUNC.
    """
    
    COLOR_CONF_EVAL_FUNC: typing.TypeAlias = typing.Callable[[NodeDiagnostics], typing.Any]
    """Color configurations used by this class must take a NodeDiagnostics argument."""


    def __init__(self, cube:RoutingCube, color_conf:ColorConf|ColorConfGroup):
        """
        Create new routing cube UI data.

        :param cube: RoutingCube
        :param color_conf: color configuration or color configuration group to use for
                           determining the face color of this node for the GUI
        """
        super().__init__(cube.position)
        self.diagnostics = cube.stats
        self.color_conf = color_conf
    

    def facecolor(self) -> tuple[float,float,float,float]:
        """
        Applies the color configuration to determine the face color this node should have
        in the GUI.

        :return: tuple of RGBA color values
        """
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


    def get_node_voxeldata(self, mode:str) -> list[RoutingCubeUIData]:
        """
        Creates and returns RoutingCubeUIData for each node in the network grid.

        :param mode: color mode (color configuration) to use
        :raises ValueError: if mode is not a valid color mode
        :return: list of RoutingCubeUIData for all nodes in the network
        """
        if mode not in VALID_COLOR_CONFS:
            raise ValueError(f"Invalid node color configuration '{mode}'")

        nodes = self.netgrid.node_list
        color_conf = NODE_COLOR_CONFS[mode]

        return [RoutingCubeUIData(node, color_conf) for node in nodes] 


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
        """
        This method is unused because the GUI handles restarting.
        """
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
            while not self.recipe.paused and num_cycles != 0:
                self.recipe.execute_next(self.netgrid)
                self.netgrid.step()

                # Automatically resume a paused recipe if pauses are ignored
                if ignore_pauses:
                    self.recipe.resume()

                # Decrement the number of cycles (will never cause the loop to exit if num_cycles < 0)    
                num_cycles -= 1            

            # Update observers with resulting end state
            self.alert_observers()

    
    def add_node(self, x:int, y:int, z:int, robot:bool=False):
        if robot:
            self.netgrid.add_robot(x, y, z)
        else:
            self.netgrid.add_node(x, y, z)
        self.alert_observers()


    def remove_node(self, x:int, y:int, z:int):
        self.netgrid.remove_node(x, y, z)
        self.alert_observers()
