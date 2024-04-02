"""
"""

class Observer:
    def __init__(self, model):
        self._model = model

    def update(self):
        raise NotImplementedError()
