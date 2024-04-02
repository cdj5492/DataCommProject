"""
https://matplotlib.org/stable/plot_types/3D/voxels_simple.html#sphx-glr-plot-types-3d-voxels-simple-py
"""

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.widgets import Button

plt.style.use('_mpl-gallery')

# Prepare some coordinates and the voxel boolean array
universe_dimensions = (8,8,8)
x, y, z = np.indices(universe_dimensions)
voxels = np.zeros(universe_dimensions)

# Define cubes (nodes)
# cube1 = (x == 2) & (y == 2) & (z == 2)
# cube2 = (x == 6) & (y == 6) & (z == 6)
# cube3 = (x == 3) & (y == 2) & (z == 2)

# Combine the objects into a single boolean array as a state
# state1 = cube1 | cube2
# state2 = state1 | cube3
state1 = voxels.copy()
state1[2,2,2] = 1
state1[6,6,6] = 1
state2 = state1.copy()
state2[3,2,2] = 1

# Sequence of network states
net_states = np.array(
    [state1, state2]
)

# Plot info
fig, ax = plt.subplots(subplot_kw={"projection":"3d"})


class Index:
    ind = 0

    def next(self, event):
        self.ind += 1

        i = self.ind % len(net_states)
        ax.cla() # Clear main axis
        ax.voxels(net_states[i], edgecolor='k') # Draw voxels on main axis
        plt.draw()

    def prev(self, event):
        self.ind -= 1

        i = self.ind % len(net_states)
        ax.cla()
        ax.voxels(net_states[i], edgecolor='k')
        plt.draw()


callback = Index()
axprev = fig.add_axes([0.7, 0.05, 0.15, 0.075]) # These axes define the button locations and sizes
axnext = fig.add_axes([0.86, 0.05, 0.1, 0.075])

bnext = Button(axnext, 'Next')
bnext.on_clicked(callback.next)
bprev = Button(axprev, 'Previous')
bprev.on_clicked(callback.prev)

# Plot the initial state
ax.voxels(net_states[0], edgecolor='k')

# ax.set(xticklabels=[],
#        yticklabels=[],
#        zticklabels=[])

plt.show()
