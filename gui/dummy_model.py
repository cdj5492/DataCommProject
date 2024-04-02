"""
"""

import numpy as np

from observer import Observer

UNIVERSE_SIZE = 8
UNIVERSE_DIMENSIONS = (UNIVERSE_SIZE,UNIVERSE_SIZE,UNIVERSE_SIZE)

class DummyNetSimulator:
    def __init__(self, max_states=10):
        self.max_states = max_states               # Maximum number of node states to track
        self.nodes = np.zeros(UNIVERSE_DIMENSIONS) # Node state
        self.idx = 0                               # Index associated with current node state
        self.node_states = list()                  # Sequence of past and present node states
        self.node_states.append(self.nodes)

        self.observers = list()


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
        """
        Get an array of the node coordinates.

        :return: node positions
        """
        return self.nodes
    

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
        Set the state to the initial state. Updates observers.
        """
        self.idx = 0
        self._update_state()
