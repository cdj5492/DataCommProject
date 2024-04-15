"""Network Simulator GUI

file: gui.py
author: Mark Danza

Graphical user interface using matplotlib, loosely based on the model-view-controller
framework.

See example:
https://matplotlib.org/stable/plot_types/3D/voxels_simple.html#sphx-glr-plot-types-3d-voxels-simple-py
"""

import dataclasses
import typing

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.figure import Figure
from matplotlib.widgets import Button, TextBox, CheckButtons

from gui.utils import Model, Observer

voxel_pos_t: typing.TypeAlias = tuple[int,int,int]
"""Typemark for voxel coordinates."""


def init_matplotlib() -> tuple[Figure, typing.Any]:
    """
    Matplotlib-related initialization.

    :return: the principal figure and axis objects
    """
    plt.style.use('_mpl-gallery')
    # Plot info
    fig, ax = plt.subplots(subplot_kw={"projection":"3d"})
    return fig, ax


@dataclasses.dataclass
class PositionHelper:
    edge : float = 0.06
    bottom : float = 0.01
    width : float = 0.14
    height : float = 0.025
    padding : float = 0.007


    def coords(self, col_from_left:int=0, row_from_bottom:int=0, split_num:int=1, split_of:int=1):
        edge = self.edge + col_from_left*(self.width + self.padding)
        bottom = self.bottom + row_from_bottom*(self.height + self.padding)
        width = (self.width - (split_of-1)*self.padding)/split_of
        height = self.height

        if split_num > 1:
            edge += (split_num - 1)*(width + self.padding)

        return edge, bottom, width, height


class PlotGUI(Observer):
    """
    GUI class.
    """
    
    def __init__(self, model:Model, colormode:str):
        super().__init__(model)    # Connection with simulator
        self.colormode = colormode # Node color configuration

        self.fig, self.ax = init_matplotlib() # Figure and axis for voxel array
        self.voxels = dict()                  # For return value of ax.voxels()

        # Other attributes used for user input
        self.run_cycles = 1000   # Number of cycles to run for
        self.ignorepause = False # Wether to ignore PAUSE commands in recipes
        self.user_node_x, self.user_node_y, self.user_node_z = 0, 0, 0
        self.user_node_robot = False

        ax_pos_helper = PositionHelper()

        # These axes define the widget locations and sizes
        ax_run_btn = self.fig.add_axes(ax_pos_helper.coords(0, 4))
        ax_cycles_txt = self.fig.add_axes(ax_pos_helper.coords(0, 3))
        ax_colormode_txt = self.fig.add_axes(ax_pos_helper.coords(0, 2))
        ax_ignorepause_chk = self.fig.add_axes(ax_pos_helper.coords(0, 1))
        ax_restart_btn = self.fig.add_axes(ax_pos_helper.coords(0, 0))
        
        ax_step_btn = self.fig.add_axes(ax_pos_helper.coords(1, 4))
        ax_x_txt = self.fig.add_axes(ax_pos_helper.coords(1, 3, split_num=1, split_of=3))
        ax_y_txt = self.fig.add_axes(ax_pos_helper.coords(1, 3, split_num=2, split_of=3))
        ax_z_txt = self.fig.add_axes(ax_pos_helper.coords(1, 3, split_num=3, split_of=3))
        ax_add_btn = self.fig.add_axes(ax_pos_helper.coords(1, 2, split_num=1, split_of=2))
        ax_remove_btn = self.fig.add_axes(ax_pos_helper.coords(1, 2, split_num=2, split_of=2))
        ax_robot_chk = self.fig.add_axes(ax_pos_helper.coords(1, 1))
        
        # Set up buttons
        self.btn_step = Button(ax_step_btn, "Step")
        self.btn_step.on_clicked(self.next)
        self.btn_run = Button(ax_run_btn, "Run")
        self.btn_run.on_clicked(self.run)
        self.btn_restart = Button(ax_restart_btn, "Reset")
        self.btn_restart.on_clicked(self.restart)
        self.btn_add = Button(ax_add_btn, "Add Node")
        self.btn_add.on_clicked(self.user_add_node)
        self.btn_remove = Button(ax_remove_btn, "Remove Node")
        self.btn_remove.on_clicked(self.user_remove_node)

        # Set up text boxes
        self.txt_cycles = TextBox(ax_cycles_txt, "Cycles", initial=str(self.run_cycles))
        self.txt_colormode = TextBox(ax_colormode_txt, "Color Mode", initial=self.colormode)
        self.txt_colormode.on_submit(self.update)
        self.txt_x = TextBox(ax_x_txt, "X", initial="0")
        self.txt_y = TextBox(ax_y_txt, "Y", initial="0")
        self.txt_z = TextBox(ax_z_txt, "Z", initial="0")

        # Set up check boxes
        self.chk_ignorepause = CheckButtons(ax_ignorepause_chk, ["Ignore Pause?"], [False])
        self.chk_robot = CheckButtons(ax_robot_chk, ["Robot Node?"], [False])
    

    def plot_voxels(self, colormode:str):
        """
        Re-plot the main axis.

        :param colormode: node color configuration to use
        """
        # Init arrays for voxel positions and face colors
        net_x, net_y, net_z = self._model.get_network_dimensions()
        voxels = np.zeros((net_x, net_y, net_z))
        facecolors = np.zeros((net_x, net_y, net_z, 4))

        # Get voxel data from model
        voxeldata = self._model.get_node_voxeldata(colormode)

        # Transfer voxel data to arrays
        for data in voxeldata:
            x, y, z = data.coordinates
            voxels[x,y,z] = 1
            facecolors[x,y,z] = data.facecolor()
        
        # Draw voxels on main axis
        self.voxels = self.ax.voxels(voxels, facecolors=facecolors, edgecolor='k', picker=True)
        plt.draw_all()


    def get_user_coords(self) -> tuple[int,int,int]|tuple[None,None,None]:
        x, y, z = self.txt_x.text, self.txt_y.text, self.txt_z.text
        vals = list()
        for val in (x, y, z):
            try:
                ival = int(val)
                if ival < 0:
                    raise ValueError
            except ValueError:
                return None, None, None
            vals.append(ival)
        return tuple(vals)


    def user_add_node(self, event):
        # Get user input from relevant widgets
        x, y, z = self.get_user_coords()
        if x is None:
            return

        robot = self.chk_robot.get_status()[0]

        # Add node to model
        self._model.add_node(x, y, z, robot=robot)


    def user_remove_node(self, event):
        # Get user input from relevant widgets
        x, y, z = self.get_user_coords()
        if x is None:
            return

        # Remove node from model
        self._model.remove_node(x, y, z)


    def next(self, event):
        """
        Advance the model to the next state.

        :param event: unused
        """
        self._model.next_state()


    def restart(self, event):
        pass


    def run(self, event):
        """
        Step through model states automatically.

        :param event: unused
        """
        # Get user input from relevant widgets
        try:
            run_cycles = int(self.txt_cycles.text)
        except ValueError:
            run_cycles = 0

        ignorepause = self.chk_ignorepause.get_status()[0]

        # Run model
        self._model.run(num_cycles=run_cycles, ignore_pauses=ignorepause)


    def update(self, event=None):
        """
        Plot the nodes in the model as voxels.
        """
        # Get user input from relevant widgets
        colormode = self.txt_colormode.text

        # Plot voxels in the window
        self.plot_voxels(colormode)
