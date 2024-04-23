"""GUI Node Color Configuration Options

file: color_conf.py
author: Mark Danza

To add a new color configuration:
 1. Define any helper functions needed by that configuration if they do not exist already.
 2. Define the color configuration as a ColorConf subclass or ColorConfGroup instance.
 3. Add the color configuration to the NODE_COLOR_CONFS dictionary in app.support.py.
Notes about creating color configurations:
 - Use ColorNormalizer, not ColorVals to specify colors.
 - In general, use None instead of 0 as a color value.
 - See gui.utils.ColorConfGroup for information on configuration priority.
"""

from gui.utils import ColorConfGroup, ColorNormalizer, ColorDefault, ColorConditional, ColorGradient
from network.routing_cube import NodeDiagnostics


def _no_pkts_received(diagnostics:NodeDiagnostics) -> bool:
    return diagnostics.num_pkts_received == 0


# Color configuration that shows a gradient for received packets
CONF_NUM_PKTS_RECEIVED = ColorConfGroup([
    # Apply a gradient from green to red based on the number of packets a node receives
    ColorGradient(
        priority=0,
        min_color=ColorNormalizer(None, 255, None), # Green
        max_color=ColorNormalizer(255, None, None), # Red
        ref_range_min=1,   # Fully green if 1 or fewer packets received
        ref_range_max=150, # Fully red if 150 or more packets received
        get_ref_val=NodeDiagnostics.get_num_pkts_received
    ),
    # Override the gradient with white color if the node received no packets
    ColorConditional(
        priority=1,
        on_color=ColorNormalizer(255, 255, 255), # White
        off_color=ColorNormalizer.null(),        # Cede to lower priority rules
        condition=_no_pkts_received
    ),
    # Apply transparency if the node is a robot
    ColorConditional(
        priority=0,
        on_color=ColorNormalizer(None, None, None, 128), # Transparent
        off_color=ColorNormalizer.null(),                # Cede to lower priority rules
        condition=NodeDiagnostics.get_is_robot
    )
])


def _any_pkts_dropped(diagnostics:NodeDiagnostics) -> bool:
    return diagnostics.num_pkts_dropped > 0


# Color a node red if it has dropped any packets, or green otherwise
CONF_ANY_PKTS_DROPPED = ColorConditional(
    priority=0,
    on_color=ColorNormalizer(255, None, None),  # Red
    off_color=ColorNormalizer(None, 255, None), # Green
    condition=_any_pkts_dropped
)


def _robot_any_pkts_sent_this_cycle(diagnostics:NodeDiagnostics) -> bool:
    return diagnostics.is_robot and diagnostics.num_pkts_sent_this_cycle > 0


def _robot_any_pkts_received_this_cycle(diagnostics:NodeDiagnostics) -> bool:
    return diagnostics.is_robot and diagnostics.num_pkts_received_this_cycle > 0


# Color configuration that shows packet flow through the network while stepping
CONF_PKT_FLOW = ColorConfGroup([
    # Color a robot node green and make it opaque, color a normal node blue and make it transparent
    ColorConditional(
        priority=1,
        on_color=ColorNormalizer(0, 255, 0, 255),  # Opaque green
        off_color=ColorNormalizer(0, 0, 255, 128), # Transparent blue
        condition=NodeDiagnostics.get_is_robot
    ),
    # Color a robot node yellow if it has sent a packet this cycle, no effect otherwise
    ColorConditional(
        priority=2,
        on_color=ColorNormalizer(255, 255, 0), # Yellow
        off_color=ColorNormalizer.null(),      # Cede to lower priority rules
        condition=_robot_any_pkts_sent_this_cycle
    ),
    # Color a robot node purple if it has received a packet this cycle, no effect otherwise
    ColorConditional(
        priority=3,
        on_color=ColorNormalizer(255, 0, 255), # Purple
        off_color=ColorNormalizer.null(),      # Cede to lower priority rules
        condition=_robot_any_pkts_received_this_cycle
    ),
    # Color a node red if it has a packet, no effect otherwise
    ColorConditional(
        priority=4,
        on_color=ColorNormalizer(255, 0, 0), # Red
        off_color=ColorNormalizer.null(),    # Cede to lower priority rules
        condition=NodeDiagnostics.get_has_packet
    ),
])
