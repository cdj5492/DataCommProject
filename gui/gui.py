"""Network Simulator GUI

file: gui.py
author: Mark Danza

Graphical user interface using matplotlib, loosely based on the model-view-controller
framework.

See example:
https://matplotlib.org/stable/plot_types/3D/voxels_simple.html#sphx-glr-plot-types-3d-voxels-simple-py
"""

import os
import typing

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.figure import Figure
from matplotlib.widgets import Button, TextBox, CheckButtons

from app.initialization import init_presenter
from gui.utils import Model, Observer, GUIContainer
from network.routing_cube import RoutingCube

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


class PlotGUI(Observer):
    """
    GUI class.
    """
    
    def __init__(self,
        model:Model,
        colormode:str,
        routing_algo_name:str,
        network_file:os.PathLike|None=None,
        recipe_file:os.PathLike|None=None
    ):
        """
        Initialize the matplotlib GUI. The caller must use the add_observer() method and
        pass in the given model to ensure this UI is updated by the model.

        :param model: network presenter model
        :param colormode: initial node color configuration
        :param routing_algo_name: routing algorithm name in case of restart
        :param network_file: optional network file path in case of restart
        :param recipe_file: optional recipe file path in case of restart
        :return: matplotlib GUI
        """
        super().__init__(model)    # Connection with simulator
        self.colormode = colormode # Node color configuration
        self.routing_algo_name = routing_algo_name
        self.network_file = network_file
        self.recipe_file = recipe_file

        self.fig, self.ax = init_matplotlib() # Figure and axis for voxel array
        self.voxels = dict()                  # For return value of ax.voxels()

        # Define containers to help with widget placement
        left_container = GUIContainer(0.06, 0.20, 0.09, 0.025, 0.007)
        right_edge = left_container.rect(1, 0)[0]
        right_container = GUIContainer(right_edge, left_container.top, 0.14, left_container.height, left_container.padding)

        # These axes define the widget locations and sizes
        left_container_axes = list()
        # Add five axes in column 0 of the left container
        for _ in range(5):
            left_container_axes.append(
                left_container.add_axes_to_fig(self.fig, column=0)
            )
        # Unpack the left container axes for use in defining widgets
        ax_run_btn, ax_cycles_txt, ax_colormode_txt, ax_ignorepause_chk, ax_restart_btn = left_container_axes
        
        # Add an axis to column 0 of the right container
        ax_step_btn = right_container.add_axes_to_fig(self.fig, column=0)
        # Add two rows of split axes to column 0 of the right container
        ax_x_txt, ax_y_txt, ax_z_txt = right_container.add_axes_to_fig(self.fig, column=0, split=3)
        ax_add_btn, ax_remove_btn = right_container.add_axes_to_fig(self.fig, column=0, split=2)
        # Add another axis to column 0 of the right container
        ax_robot_chk = right_container.add_axes_to_fig(self.fig, column=0)
        
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
        self.txt_cycles = TextBox(ax_cycles_txt, "Cycles", initial=str(1000))
        self.txt_colormode = TextBox(ax_colormode_txt, "Color Mode", initial=self.colormode)
        self.txt_colormode.on_submit(self.update)
        self.txt_x = TextBox(ax_x_txt, "X", initial="0")
        self.txt_y = TextBox(ax_y_txt, "Y", initial="0")
        self.txt_z = TextBox(ax_z_txt, "Z", initial="0")

        # Set up check boxes
        self.chk_ignorepause = CheckButtons(ax_ignorepause_chk, ["Ignore Pause?"], [False])
        self.chk_robot = CheckButtons(ax_robot_chk, ["Robot Node?"], [False])

        # Set axis used to display text on network stats
        self.ax_statstxt = self.fig.add_axes([0.01, 0.99, 0.30, 0.20])
    

    def plot_voxels(self, colormode:str):
        """
        Re-plot the main axis.

        :param colormode: node color configuration to use
        """
        # Clear main axis
        self.ax.cla()

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

        # Get stats text for GUI
        statstext_properties = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
        statstext = str(self._model.netgrid.stats)
        statstext = '\n'.join([
            "Simulation Info.",
            "-"*60,
            f"Cycle Number: {self._model.cycle_num}",
            f"Node Queue Size: {RoutingCube.MAX_Q_LEN}",
            "-"*60,
            statstext,
        ])

        # Set stats text
        self.ax_statstxt.cla()
        self.ax_statstxt.set_axis_off()
        self.ax_statstxt.text(
            0.0, 0.0,
            statstext,
            transform=self.ax_statstxt.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=statstext_properties
        )
        
        # Draw voxels on main axis
        self.voxels = self.ax.voxels(voxels, facecolors=facecolors, edgecolor='k', picker=True)
        plt.draw()


    def get_user_coords(self) -> tuple[int,int,int]|tuple[None,None,None]:
        """
        Helper method for reading the x,y,z coordinates the user has typed into the
        associated text fields.

        :return: x,y,z node coordinates or None,None,None if any of the user coordinates
        are invalid
        """
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
        """
        Add a node to the network at the user-specified coordinates. May be a robot node
        if the robot check box is checked.

        :param event: unused
        """
        # Get user input from relevant widgets
        x, y, z = self.get_user_coords()
        if x is None:
            return

        robot = self.chk_robot.get_status()[0]

        # Add node to model
        self._model.add_node(x, y, z, robot=robot)


    def user_remove_node(self, event):
        """
        Remove a node from the network at the user-specified coordinates.

        :param event: unused
        """
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
        """
        Restart by initializing a new model to replace the current one.

        :param event: unused
        """
        size = self._model.get_network_dimensions()
        self._model = init_presenter(self.routing_algo_name, self.network_file, self.recipe_file, size[0])
        self._model.add_observer(self)


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
