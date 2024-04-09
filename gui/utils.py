"""GUI Utility Classes

file: utils.py
author: Mark Danza

Contains interface-like class definitions for the Observer and Model types.
"""

import numpy as np


class Observer:
    """
    Object whose state can be updated by a model.
    """

    def __init__(self, model):
        """
        Create a new object watching the given model.

        :param model: model that updates this observer
        """
        self._model = model

    def update(self):
        """
        Update using the stored model.

        :raises NotImplementedError: if not implemented in a subclass
        """
        raise NotImplementedError()


class Model:
    """
    Object responsible for a network simulation.
    """

    def __init__(self):
        """
        Creates a presenter for the given grid.

        :param netgrid: simulator backend
        :param dimensions: (x, y, z) dimensions of grid to plot the network in
        """
        #self.netgrid = netgrid
        #self.dimensions = dimensions
        #super().__init__()
        self._observers = list()
    #def get_node_positions(self) -> np.ndarray[int]:
        #need this
        #node_map = self.netgrid.node_map
        #nodes = np.zeros(self.dimensions, dtype=int)

        #for x, y, z in node_map.keys():
         #   nodes[x, y, z] = 1

        #return nodes

    def get_node_facecolors(self) -> np.ndarray[str]:
        """
        Nodes containing packets are colored red. All other nodes are blue.
        """
        node_map = self.netgrid.node_map
        node_facecolors = np.full(self.dimensions, COLOR_BLUE, dtype=str)

        for (x, y, z), node in node_map.items():
            if _node_has_packet(node):
                node_facecolors[x, y, z] = COLOR_RED

        return node_facecolors



    def alert_observers(self):
        """
        Call the update() method of all this model's observers.
        """
        for obs in self._observers:
            obs.update()


    def add_observer(self, obs:Observer):
        """
        Add the given object to this model's observer list.

        :param obs: observer
        """
        self._observers.append(obs)
        self.alert_observers()


    def get_node_positions(self) -> np.ndarray[int]:
        """
        Construct a 3D array representing the network, with a truthy value at every
        (x,y,z) coordinate where there is a node present.

        :raises NotImplementedError: if not implemented in a subclass
        :return: array indicating node positions for drawing voxels
        """
        raise NotImplementedError()
    

    def get_node_facecolors(self) -> np.ndarray[str]|None:
        """
        Construct a 3D array with a matplotlib color code at each (x,y,z) coordinate that
        corresponds to the position of a node.

        This method may return None to inidcate the use of default facecolors.

        :raises NotImplementedError: if not implemented in a subclass
        :return: array indicating node colors for drawing voxels
        """
        raise NotImplementedError()


    def next_state(self):
        """
        Step the simulator and graphics to the next network state in time. 

        REQUIREMENT: This method should call alert_observers() if it is used.

        :raises NotImplementedError: if not implemented in a subclass
        """
        self.netgrid.step()
        self.alert_observers()
        raise NotImplementedError()
    

    def prev_state(self):
        """
        Step the simulator and graphics to the previous network state. 

        REQUIREMENT: This method should call alert_observers() if it is used.

        :raises NotImplementedError: if not implemented in a subclass
        """
        raise NotImplementedError()
    

    def restart(self):
        """
        Reset the simulator and graphics to the initial network state.

        REQUIREMENT: This method should call alert_observers() if it is used.

        :raises NotImplementedError: _description_
        """
        # Constants 
        COLOR_BLUE = "blue"
        COLOR_RED = "red"
        raise NotImplementedError()
