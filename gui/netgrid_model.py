"""Model Class for NetworkGrid Simulator

file: netgrid_model.py
author: Mark Danza

This contains a class which encapsulates a NetworkGrid object with the functions required
for any network simulator Model.
"""

import typing

import numpy as np

from gui.utils import VoxelData, Model, ColorConf, ColorConfGroup, ColorNormalizer, ColorConditional, ColorGradient
from network.network_grid import NetworkGrid
from network.robot import Robot
from network.routing_cube import RoutingCube
from network.sim.recipe import Recipe

NODE_COLOR_CONF = {
    "num_pkts_received" : ColorConfGroup([
        ColorGradient(
            priority=0,
            min_color=ColorNormalizer(None, 255, None),
            max_color=ColorNormalizer(255, None, None),
            ref_range_min=1,
            ref_range_max=150
        ),
        ColorConditional(
            priority=1,
            on_color=ColorNormalizer(255, 255, 255),
            off_color=ColorNormalizer.NULL,
            condition=lambda num_pkts : num_pkts == 0
        )
    ]),
    "num_pkts_dropped" : ColorConditional(
        priority=0,
        on_color=ColorNormalizer(255, None, None),
        off_color=ColorNormalizer(None, 255, None),
        condition=lambda num_pkts : num_pkts > 0
    ),
    "show_pkt_flow" : ColorConfGroup([
        # Red if has packet, blue and transparent otherwise
        ColorConditional(
            priority=0,
            on_color=ColorNormalizer(255, None, None),
            off_color=ColorNormalizer(None, None, 255, 128),
            condition=lambda cube_flow_data : cube_flow_data[0]
        ),
        # Green and opaque if robot, overridden by lower priority rule otherwise
        ColorConditional(
            priority=1,
            on_color=ColorNormalizer(0, 255, 0, 255),
            off_color=ColorNormalizer.NULL,
            condition=lambda cube_flow_data : cube_flow_data[1]
        ),
    ])
}


class RoutingCubeVoxelData(VoxelData):
    # TODO (placeholder) condition : typing.Callable[[RoutingCube], bool]|None = None
    EXTRA_METRICS = ["show_pkt_flow"]


    def __init__(self, cube:RoutingCube, color_confs:dict[str, ColorConf|ColorConfGroup]):
        super().__init__(cube.position)
        self.diagnostics = cube.stats
        self.cube_has_pkt = cube.has_packet()

        for metric in color_confs.keys():
            if metric not in RoutingCubeVoxelData.EXTRA_METRICS:
                # Intentionally allow AttributeError with any invalid metric
                self._get_metric_value(metric)

        self.color_confs = color_confs


    def _get_metric_value(self, metric:str) -> typing.Any:
        if metric == "show_pkt_flow":
            return self.cube_has_pkt, self.diagnostics.is_robot

        try:
            return getattr(self.diagnostics, metric)
        except AttributeError as e:
            e.add_note(f"'{metric}' is an invalid metric for RoutingCubeVoxelData")
            raise e
    

    def facecolor(self, metric:str) -> tuple[float,float,float,float]:
        value = self._get_metric_value(metric)
        
        try:
            conf = self.color_confs[metric]
        except KeyError as e:
            e.add_note(f"No color configuration provided for metric '{metric}' in RoutingCubeVoxelData")
            raise e
        
        return conf(value).vals()


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


    def get_node_voxeldata(self) -> list[RoutingCubeVoxelData]:
        nodes = self.netgrid.node_list
        return [RoutingCubeVoxelData(node, NODE_COLOR_CONF) for node in nodes]
    

    # TODO move to GUI
    def get_node_facecolors(self) -> np.ndarray[str]:
        """
        Nodes containing packets are colored red. Nodes representing robot connection
        points are colored green. All other nodes are blue.
        """
        node_map = self.netgrid.node_map
        node_facecolors = np.zeros(self.dimensions, dtype=str)

        for (x,y,z), node in node_map.items():
            if node.has_packet():
                node_facecolors[x,y,z] = COLOR_RED
            elif _node_is_robot(node, self.netgrid.robot_list):
                node_facecolors[x,y,z] = COLOR_GREEN
            else:
                node_facecolors[x,y,z] = COLOR_BLUE 

        return node_facecolors


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
