"""Network Simulator GUI

file: gui.py
author: Mark Danza

Graphical user interface using matplotlib, loosely based on the model-view-controller
framework.

See example:
https://matplotlib.org/stable/plot_types/3D/voxels_simple.html#sphx-glr-plot-types-3d-voxels-simple-py
"""

import typing

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.figure import Figure
from matplotlib.widgets import Button

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


class PlotGUI(Observer):
    """
    GUI class.
    """
    
    def __init__(self, model:Model, dimensions:tuple[int,int,int], colormode:str):
        super().__init__(model)      # Connection with simulator
        self.dimensions = dimensions # Universe dimensions
        self.colormode = colormode   # Node color configuration

        self.fig, self.ax = init_matplotlib() # Figure and axis for voxel array

        ax_run_btn = self.fig.add_axes([0.75, 0.08, 0.10, 0.075]) # These axes define the button locations and sizes
        ax_step_btn = self.fig.add_axes([0.86, 0.08, 0.10, 0.075])
        # ax_skip_to_end_btn = self.fig.add_axes([0.7, 0.0, 0.15, 0.075])

        # Set up buttons
        self.btn_step = Button(ax_step_btn, "Step")
        self.btn_step.on_clicked(self.next)
        self.btn_run = Button(ax_run_btn, "Run")
        self.btn_run.on_clicked(self.run)
        # self.btn_skip_to_end = Button(ax_skip_to_end_btn, "Skip to End")
        # self.btn_skip_to_end.on_clicked(self.skip_to_end)
    

    def plot_voxels(self, colormode:str):
        """
        Re-plot the main axis.

        :param colormode: node color configuration to use
        """
        self.ax.cla() # Clear main axis

        net_x, net_y, net_z = self._model.get_network_dimensions()
        voxels = np.zeros((net_x, net_y, net_z))
        facecolors = np.zeros((net_x, net_y, net_z, 4))

        voxeldata = self._model.get_node_voxeldata(colormode)

        for data in voxeldata:
            x, y, z = data.coordinates
            voxels[x,y,z] = 1
            facecolors[x,y,z] = data.facecolor()
        
        self.ax.voxels(voxels, facecolors=facecolors, edgecolor='k') # Draw voxels on main axis
        plt.draw()


    def next(self, event):
        """
        Advance the model to the next state.

        :param event: unused
        """
        self._model.next_state()


    def run(self, event):
        """
        Step through model states automatically.

        :param event: unused
        """
        self._model.run()


    def update(self):
        """
        Plot the nodes in the model as voxels.
        """
        self.plot_voxels(self.colormode)
