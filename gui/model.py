"""
"""

import numpy as np

from observer import Observer

class Model:
    def __init__(self):
        self._observers = list()


    def alert_observers(self):
        """
        Call the update() method of all this model's observers.
        """
        for obs in self.observers:
            obs.update()


    def add_observer(self, obs:Observer):
        """
        Add the given object to this model's observer list.

        :param obs: observer
        """
        self.observers.append(obs)
        self.alert_observers()


    def get_nodes(self) -> np.ndarray[tuple[int,int,int]]:
        raise NotImplementedError()


    def next_state(self):
        raise NotImplementedError()
    

    def prev_state(self):
        raise NotImplementedError()
    

    def restart(self):
        raise NotImplementedError()
