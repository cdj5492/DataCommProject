"""GUI Utility Classes

file: utils.py
author: Mark Danza

Contains interface-like class definitions for the Observer and Model types. Also contains
the node color configuration framework for defining GUI color modes and a helper class
for setting up the matplotlib GUI.
"""

import dataclasses
import typing

import matplotlib.colors
from matplotlib.figure import Figure

#########################################################################################
# MVC Interface
#########################################################################################


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


class NodeUIData:
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


    def get_node_voxeldata(self, *args, **kwargs) -> typing.Collection[NodeUIData]:
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
    

#########################################################################################
# Node Color Configuration Framework
#########################################################################################


class ColorVals:
    """
    RGBA color values. This class exists to provide a more sophisticated way for storing
    these values together in color configurations.

    This class is an iterable which iterates over its RGBA values, in that order.
    """

    DEFAULT_RGB : float = 0.0
    """Default normalized value of red, green, and blue."""
    DEFAULT_ALPHA : float = 1.0
    """Default normalized value of alpha."""


    def __init__(self, r:float|None, g:float|None, b:float|None, a:float|None=None):
        """
        Create new color values. RGBA values may be any number, relative to one another.
        These values can be normalized using a ColorNormalizer. These values may be None.

        :param r: red value
        :param g: green value
        :param b: blue value
        :param a: alpha value
        """
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        self.__next_val = 0


    def vals(self) -> tuple[float,float,float,float]:
        """
        Gets the RGBA values, replacing values of None with their associated default
        values.

        :return: tuple of RGBA color values
        """
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
    """
    Encapsulates color values (a ColorVals instance) with a matplotlib color normalizer
    for mapping those values onto the range [0.0, 1.0].
    """

    def __init__(self, r:float|None, g:float|None, b:float|None, a:float|None=None, min_rgba_val:float=0.0, max_rgba_val:float=255.0):
        """
        Create a new color normalizer.

        :param r: red value
        :param g: green value
        :param b: blue value
        :param a: alpha value
        :param min_rgba_val: minimum RGBA value, which will be normalized to 0.0
        :param max_rgba_val: maximum RGBA value, which will be normalized to 1.0
        """
        self.colors = ColorVals(r, g, b, a)
        self.min_rgba_val = min_rgba_val
        self.max_rgba_val = max_rgba_val


    def get_normalized(self) -> ColorVals:
        """
        Get the normalized versions of the RGBA color values. Values of None will remain
        as None in the color values returned by this method.

        :return: RGBA color values
        """
        normalizer = matplotlib.colors.Normalize(vmin=self.min_rgba_val, vmax=self.max_rgba_val, clip=True)

        colors = list()
        for val in self.colors:
            if val is not None:
                colors.append(normalizer(val))
            else:
                colors.append(None)

        return ColorVals(*colors)
    

    @classmethod
    def null(cls):
        """
        Helper method for instantiating the "null color", or a color normalizer with all
        the color values set to None.

        :return: null color
        """
        return cls(None, None, None, None)


@dataclasses.dataclass
class ColorConf:
    """
    Color configuration for network nodes. Calling an instance of this class should
    return color values as dictated by the configuration type.
    """
    priority : int # Priority of this color configuration in a ColorConfGroup


    def __call__(self, *args, **kwargs) -> ColorVals:
        """
        :raises NotImplementedError: if not implemented in a subclass
        :return: RGBA color values
        """
        raise NotImplementedError()


@dataclasses.dataclass
class ColorConfGroup:
    """
    Group of color configurations which are allowed to take priority over one another.
    Calling an instance of this class calls all the configurations in the group to get
    their color values. These color values are then combined according to the priorities
    of their respective configurations:
    - Non-None values of higher priority will supercede all values of lower priority.
    - Non-None values of lower priority will supercede None-values of higher or equal
      priority.
    - Non-None values of equal priority should not be used to ensure predictable
      behavior.
    - Values which are None in all color configurations will remain None.
    - Minimum priority is 0.
    """
    confs : list[ColorConf]


    def __call__(self, *args, **kwargs) -> ColorVals:
        colors = [conf(*args, **kwargs) for conf in self.confs]
        priorities = [conf.priority for conf in self.confs]

        result = [None, None, None, None]
        result_priority = 0
        
        for color, priority in zip(colors, priorities):
            if priority > result_priority:
                # Overwrite result rgba values with higher priority (non-None) rgba values
                for i, val in enumerate(color):
                    if val is not None:
                        result[i] = val
                # Increase priority level of result color
                result_priority = priority
            else:
                # Overwrite a value if the result value is None and the new one is not
                for i, val in enumerate(color):
                    if result[i] is None and val is not None:
                        result[i] = val
        
        return ColorVals(*result)
    

@dataclasses.dataclass
class ColorConditional(ColorConf):
    """
    Color configuration that operates on a conditional function. Calling an instance of
    this class calls the condition function with all the given arguments, and returns the
    normalized values of on_color or off_color accordingly.
    """
    on_color : ColorNormalizer  # Color to use when the condition is True
    off_color : ColorNormalizer # Color to use when the condition is False
    condition : typing.Callable[[typing.Any], bool] # Condition function


    def __call__(self, *args, **kwargs) -> ColorVals:
        if self.condition(*args, **kwargs):
            return self.on_color.get_normalized()
        else:
            return self.off_color.get_normalized()


@dataclasses.dataclass
class ColorGradient(ColorConf):
    """
    Color configuration that provides a gradient from one color to another based on some
    reference value. Calling an instance of this class calls the reference value getter
    function with all the given arguments, calculates the color values between min_color
    and max_color corresponding to the referece value, and returns the normalized color
    values of the resulting color.
    """
    min_color : ColorNormalizer # Color at the "bottom" of the gradient
    max_color : ColorNormalizer # Color at the "top" of the gradient
    ref_range_min : float       # Minimum possible reference value, corresponding to min_color
    ref_range_max : float       # Maximum possible reference value, corresponding to max_color
    get_ref_val : typing.Callable[[typing.Any], float] # Function that gets the reference value


    def __call__(self, *args, **kwargs) -> ColorVals:
        norm_min_color = self.min_color.get_normalized()
        norm_max_color = self.max_color.get_normalized()
        
        ref_val = self.get_ref_val(*args, **kwargs)
        ref_normalizer = matplotlib.colors.Normalize(vmin=self.ref_range_min, vmax=self.ref_range_max, clip=True)
        norm_ref_val = ref_normalizer(ref_val)

        gradient_diff = list()
        for real_min, real_max, min_val, max_val, in zip(norm_min_color, norm_max_color, norm_min_color.vals(), norm_max_color.vals()):
            if real_min is None and real_max is None:
                gradient_diff.append(None)
            else:
                gradient_diff.append(max_val - min_val)

        gradient_color = list()
        for grad, min_val in zip(gradient_diff, norm_min_color.vals()):
            if grad is not None:
                gradient_color.append(norm_ref_val*grad + min_val)
            else:
                gradient_color.append(None)

        return ColorVals(*gradient_color)
    

#########################################################################################
# GUI Utilities
#########################################################################################
    

class GUIContainer:
    """
    Helper class for grouping together the axes for Matplotlib widgets and automatically
    calculating the "rects" (left, bottom, width, height tuples) for instantiating new
    axes. The user provides initial axes dimensions when instantiating this class. Then,
    this class can be used to "append" axes to a figure in the spaces represented by
    columns of the container. Each container column represents a vertical section of
    axes regions, where each row represents a rect of the specified width and height.
    """

    def __init__(self, edge:float, top:float, width:float, height:float, padding:float):
        """
        Initialize a container representing a region in the plot. All arguments should be
        in the range [0.0, 1.0].

        :param edge: coordinate of left edge of container region
        :param top: coordinate of top edge of container region
        :param width: coordinate representing the width of the container region's rects
                      (provides the width of each axes within the container)
        :param height: coordinate representing the height of the container region's rects
                       (provides the height of each axes within the container)
        :param padding: padding amount between rects (between columns and rows of the
                        container)
        """
        self.edge = edge
        self.top = top
        self.width = width
        self.height = height
        self.padding = padding
        self._columns = dict()


    def rect(self, col_from_left:int=0, row_from_top:int=0, split_num:int=1, split_of:int=1):
        """
        Get the rect coordinates of the subregion of the container represented by the
        given column and row.

        The split_num and split_of parameters may be used to split a container rect into
        a number of smaller rects given by split_of. If split_of > 1, the split_num
        parameter then specifies the split subregion, starting from 1 on the left.

        :param col_from_left: container column index, starting from 0 on the left
        :param row_from_top: container row index, starting from 0 at the top
        :param split_num: split number <= split_of, starting from 1 on the left
        :param split_of: number of subrects to split this rect into, >= 1
        :return: edge, bottom, width, height
        """
        edge = self.edge + col_from_left*(self.width + self.padding)
        bottom = self.top - (row_from_top + 1)*(self.height + self.padding)
        width = (self.width - (split_of-1)*self.padding)/split_of
        height = self.height

        # Move edge to the right to account for the split
        if split_num > 1:
            edge += (split_num - 1)*(width + self.padding)

        return edge, bottom, width, height
    

    def get_next_rects(self, column:int=0, split:int=1) -> list[tuple[float,float,float,float]]:
        """
        Calculates the next rect or rects that should occur in the given column. This is
        a convenience method so that the user need not call rect() to get each individual
        rect in a column of the container.

        If split > 1, this method calculates all the subrects of the split region and
        returns them in a list. Otherwise, a single rect will be returned in a list.

        :param column: container column index, starting from 0 on the left
        :param split: number of subrects to split the next rect into, >= 1
        :return: list of rects
        """
        # Columns are tracked internally in a dict, indexed by the column number
        if column not in self._columns:
            self._columns[column] = dict()
        axis_col = self._columns[column]

        # Obtain the next row number in the specified column
        row = len(axis_col)

        # Calculate the rects in this row
        rects = list()
        for i in range(1, split+1):
            rects.append(self.rect(column, row, split_num=i, split_of=split))

        # Internally store and return the calculated rects
        axis_col[row] = rects
        return rects
    

    def add_axes_to_fig(self, fig:Figure, column:int=0, split:int=1) -> typing.Any|list:
        """
        Convenience method that calls get_next_rects() and adds axes to the given figure
        using the resulting rects.

        :param fig: matplotlib figure
        :param column: container column index, starting from 0 on the left
        :param split: number of subrects to split the next rect into, >= 1
        :return: matplotlib axes object (or a list of them) added to the figure
        """
        axes = list()
        for rect in self.get_next_rects(column, split):
            axes.append(fig.add_axes(rect))

        if len(axes) == 1:
            axes = axes[0]
        return axes
