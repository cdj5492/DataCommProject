"""GUI Node Color Configuration Options

file: color_conf.py
author: Mark Danza
"""

from gui.utils import ColorConfGroup, ColorNormalizer, ColorConditional, ColorGradient
from network.routing_cube import NodeDiagnostics


def _no_pkts_received(diagnostics:NodeDiagnostics) -> bool:
    return diagnostics.num_pkts_received == 0


_CONF_NUM_PKTS_RECEIVED = ColorConfGroup([
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
    )
])


def _any_pkts_dropped(diagnostics:NodeDiagnostics) -> bool:
    return diagnostics.num_pkts_dropped > 0


# Color a node red if it has dropped any packets, or green otherwise
_CONF_ANY_PKTS_DROPPED = ColorConditional(
    priority=0,
    on_color=ColorNormalizer(255, None, None),  # Red
    off_color=ColorNormalizer(None, 255, None), # Green
    condition=_any_pkts_dropped
)


_CONF_PKT_FLOW = ColorConfGroup([
    # Color a node red if it has a packet, or blue and transparent otherwise
    ColorConditional(
        priority=0,
        on_color=ColorNormalizer(255, None, None),       # Red
        off_color=ColorNormalizer(None, None, 255, 128), # Transparent blue
        condition=NodeDiagnostics.get_has_packet
    ),
    # Color a node green and opaque if it's a robot, no effect otherwise
    ColorConditional(
        priority=1,
        on_color=ColorNormalizer(0, 255, 0, 255), # Opaque green
        off_color=ColorNormalizer.null(),         # Cede to lower priority rules
        condition=NodeDiagnostics.get_is_robot
    ),
])


NODE_COLOR_CONFS = {
    "pkt-rx" : _CONF_NUM_PKTS_RECEIVED,
    "pkt-drop" : _CONF_ANY_PKTS_DROPPED,
    "pkt-flow" : _CONF_PKT_FLOW,
}

VALID_COLOR_CONFS = set(NODE_COLOR_CONFS.keys())
