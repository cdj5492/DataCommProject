"""GUI Utility Classes
"""

import numpy as np


class Observer:
    def __init__(self, model):
        self._model = model

    def update(self):
        raise NotImplementedError()


class Model:
    def __init__(self):
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
        raise NotImplementedError()
    

    def get_node_facecolors(self) -> np.ndarray[str]:
        raise NotImplementedError()


    def next_state(self):
        raise NotImplementedError()
    

    def prev_state(self):
        raise NotImplementedError()
    

    def restart(self):
        raise NotImplementedError()
