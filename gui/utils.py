"""GUI Utility Classes

file: utils.py
author: Mark Danza

Contains interface-like class definitions for the Observer and Model types.
"""

import dataclasses
import typing

import matplotlib.colors


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


class NodeData:
    """
    Data about a node that is used by the user interface.
    """

    def __init__(self, coordinates:tuple[int,int,int]):
        """
        Create new node data.

        :param coordinates: x,y,z coordinates of the node in the network
        """
        self.coordinates = coordinates


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


    def get_network_dimensions(self, *args, **kwargs) -> tuple[int,int,int]:
        """
        Gets the x, y, z dimensions of the network.

        :raises NotImplementedError: if not implemented in a subclass
        """
        raise NotImplementedError()


    def get_node_voxeldata(self, *args, **kwargs) -> typing.Collection[NodeData]:
        """
        Gets the voxel data of the network relevant to the UI.

        :raises NotImplementedError: if not implemented in a subclass
        """
        raise NotImplementedError()


    def next_state(self, *args, **kwargs) -> typing.Any:
        """
        Step the simulator and graphics to the next network state in time. 

        REQUIREMENT: This method should call alert_observers() if it is used.

        :raises NotImplementedError: if not implemented in a subclass
        """
        raise NotImplementedError()
    

    def restart(self, *args, **kwargs) -> typing.Any:
        """
        Reset the simulator and graphics to the initial network state.

        REQUIREMENT: This method should call alert_observers() if it is used.

        :raises NotImplementedError: if not implemented in a subclass
        """
        raise NotImplementedError()
    

    def run(self, *args, **kwargs) -> typing.Any:
        """
        Step through the entire simulation or a subset of it and update with the final
        state.

        REQUIREMENT: This method should call alert_observers() if it is used.

        :param kwargs: model-specific keyword arguments provided by the UI
        :raises NotImplementedError: if not implemented in a subclass
        """
        raise NotImplementedError()
    

    def add_node(self, *args, **kwargs) -> typing.Any:
        """
        Add a node to the network.

        REQUIREMENT: This method should call alert_observers() if it is used.

        :raises NotImplementedError: if not implemented in a subclass
        """
        raise NotImplementedError()
    

    def remove_node(self, *args, **kwargs) -> typing.Any:
        """
        Remove a node from the network.

        REQUIREMENT: This method should call alert_observers() if it is used.

        :raises NotImplementedError: if not implemented in a subclass
        """
        raise NotImplementedError()


class ColorVals:
    DEFAULT_RGB : float = 0.0
    DEFAULT_ALPHA : float = 1.0


    def __init__(self, r:float|None, g:float|None, b:float|None, a:float|None=None):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        self.__next_val = 0


    def vals(self) -> tuple[float,float,float,float]:
        colors = list()
        # Get rgb values or default
        for val in (self.r, self.g, self.b):
            if val is not None:
                colors.append(val)
            else:
                colors.append(ColorVals.DEFAULT_RGB)

        # Get alpha value or default
        if self.a is not None:
            colors.append(self.a)
        else:
            colors.append(ColorVals.DEFAULT_ALPHA)
        
        return tuple(colors)
    

    def __iter__(self):
        return self
    

    def __next__(self):
        self.__next_val += 1
        if self.__next_val == 1:
            return self.r
        elif self.__next_val == 2:
            return self.g
        elif self.__next_val == 3:
            return self.b
        elif self.__next_val == 4:
            return self.a
        else:
            self.__next_val = 0
            raise StopIteration


class ColorNormalizer:
    def __init__(self, r:float|None, g:float|None, b:float|None, a:float|None=None, min_rgba_val:float=0.0, max_rgba_val:float=255.0):
        self.colors = ColorVals(r, g, b, a)
        self.min_rgba_val = min_rgba_val
        self.max_rgba_val = max_rgba_val


    def get_normalized(self) -> ColorVals:
        normalizer = matplotlib.colors.Normalize(vmin=self.min_rgba_val, vmax=self.max_rgba_val, clip=True)

        colors = list()
        for val in (self.colors.r, self.colors.g, self.colors.b, self.colors.a):
            if val is not None:
                colors.append(normalizer(val))
            else:
                colors.append(None)

        return ColorVals(*colors)
    

    @classmethod
    def null(cls):
        return cls(None, None, None, None)


@dataclasses.dataclass
class ColorConf:
    priority : int


    def __call__(self, *args, **kwargs) -> ColorVals:
        raise NotImplementedError()


@dataclasses.dataclass
class ColorConfGroup:
    confs : list[ColorConf]


    def __call__(self, *args, **kwargs) -> ColorVals:
        colors = list()
        priorities = list()

        for conf in self.confs:
            colors.append(conf(*args, **kwargs))
            priorities.append(conf.priority)

        result = [None, None, None, None]
        current_priority = 0
        
        for color, priority in zip(colors, priorities):
            if priority > current_priority:
                # Overwrite current rgba values with higher priority (non-None) rgba values
                for i, val in enumerate(color):
                    if val is not None:
                        result[i] = val
                # Increase priority level of current color
                current_priority = priority
            else:
                # Overwrite a value if the current value is None and the new one is not
                for i, val in enumerate(color):
                    if result[i] is None and val is not None:
                        result[i] = val
        
        return ColorVals(*result)
    

@dataclasses.dataclass
class ColorConditional(ColorConf):
    on_color : ColorNormalizer
    off_color : ColorNormalizer
    condition : typing.Callable[[typing.Any], bool]


    def __call__(self, *args, **kwargs) -> ColorVals:
        if self.condition(*args, **kwargs):
            return self.on_color.get_normalized()
        else:
            return self.off_color.get_normalized()


@dataclasses.dataclass
class ColorGradient(ColorConf):
    min_color : ColorNormalizer
    max_color : ColorNormalizer
    ref_range_min : float
    ref_range_max : float
    get_ref_val : typing.Callable[[typing.Any], float]


    def __call__(self, *args, **kwargs) -> ColorVals:
        norm_min_color = self.min_color.get_normalized()
        norm_max_color = self.max_color.get_normalized()
        
        ref_val = self.get_ref_val(*args, **kwargs)
        ref_normalizer = matplotlib.colors.Normalize(vmin=self.ref_range_min, vmax=self.ref_range_max, clip=True)
        norm_ref_val = ref_normalizer(ref_val)

        gradient_diff = list()
        for real_min, real_max, min_val, max_val, in zip(norm_min_color, norm_max_color, norm_min_color.vals(), norm_max_color.vals()):
            if real_min is None and real_max is None:
                gradient_diff.append(0)
            else:
                gradient_diff.append(max_val - min_val)

        gradient_color = list()
        for grad, min_val in zip(gradient_diff, norm_min_color.vals()):
            gradient_color.append(norm_ref_val*grad + min_val)

        return ColorVals(*gradient_color)
