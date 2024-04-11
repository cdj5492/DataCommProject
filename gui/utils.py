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
        """
        self._observers = list()


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

        :raises NotImplementedError: if not implemented in a subclass
        """
        raise NotImplementedError()
    

    def run(self):
        """
        Step through the entire simulation or a subset of it and update with the final
        state.

        REQUIREMENT: This method should call alert_observers() if it is used.

        :raises NotImplementedError: if not implemented in a subclass
        """
        # TODO 'run diagnostics' feature
        # Running diagnostics allows the user to run the simulation for some specified
        # number of cycles, keeping track of node metrics like number of packets
        # processed, power consumed, collisions, etc.
        raise NotImplementedError()
