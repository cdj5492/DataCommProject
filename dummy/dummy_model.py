"""Fake Network Simulator Model for GUI Testing

file: dummy_model.py
author: Mark Danza
"""

import numpy as np

from gui.utils import Model

UNIVERSE_SIZE = 8
UNIVERSE_DIMENSIONS = (UNIVERSE_SIZE,UNIVERSE_SIZE,UNIVERSE_SIZE)


class DummyNetSimulator(Model):
    """
    Dummy model that generates and adds random nodes.
    """

    def __init__(self, max_states=10):
        self.max_states = max_states               # Maximum number of node states to track
        self.nodes = np.zeros(UNIVERSE_DIMENSIONS) # Node state
        self.idx = 0                               # Index associated with current node state
        self.node_states = list()                  # Sequence of past and present node states
        self.node_states.append(self.nodes)
        super().__init__()

    
    def get_node_positions(self) -> np.ndarray[int]:
        return self.nodes
    

    def get_node_facecolors(self) -> None:
        """
        Use default facecolors.

        :return: None
        """
        return None
    

    def _update_state(self):
        """
        Update the active state. Creates a new state with a new random node if the number
        of saved states is less than the maximum number of states. Updates observers.
        """
        # Add new node randomly
        if len(self.node_states) < self.max_states:
            rand_node = np.random.randint(0, UNIVERSE_SIZE-1, size=3)

            new_state = np.copy(self.node_states[-1])
            new_state[rand_node[0],rand_node[1],rand_node[2]] = 1

            self.node_states.append(new_state)

        # Get appropriate index and current state, then update observers
        i = self.idx % len(self.node_states)
        self.nodes = self.node_states[i]

        self.alert_observers()
    

    def next_state(self):
        """
        Make the next state active. Updates observers.
        """
        self.idx += 1
        self._update_state()


    def prev_state(self):
        """
        Make the previous state active. Updates observers.
        """
        self.idx -= 1
        self._update_state()

    
    def restart(self):
        """
        Set the active state to the initial state. Updates observers.
        """
        self.idx = 0
        self._update_state()


    def run(self):
        """
        Restart and then run simulation to end state.
        """
        self.restart()
        while self.idx < self.max_states - 1:
            self.next_state()
