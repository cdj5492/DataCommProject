"""Class for Tracking Network-Wide Statistics

file: netstats.py
author: Mark Danza
"""

import dataclasses
import io

from network.routing_cube import NodeDiagnostics
    

@dataclasses.dataclass
class NetworkDiagnostics:
    # Network statistics
    total_pkts_sent : int = 0
    total_pkts_sent_this_cycle : int = 0
    total_pkts_received : int = 0
    total_pkts_received_this_cycle : int = 0
    total_pkts_dropped : int = 0
    total_pkts_dropped_this_cycle : int = 0
    total_pkts_queued : int = 0
    correctly_routed_pkts : int = 0

    # Per-node statistics
    max_total_pkts_sent : int = 0
    max_pkts_sent_this_cycle : int = 0
    max_total_pkts_received : int = 0
    max_pkts_received_this_cycle : int = 0
    max_total_pkts_dropped : int = 0
    max_pkts_dropped_this_cycle : int = 0
    max_node_memory_usage : int = 0
    max_node_memory_usage_this_cycle : int = 0
    max_current_q_len : int = 0
    max_highest_q_len : int = 0


    def reset_cycle_dependent_stats(self):
        # Network-wide
        self.total_pkts_sent_this_cycle = 0
        self.total_pkts_received_this_cycle = 0
        self.total_pkts_dropped_this_cycle = 0
        self.total_pkts_queued = 0

        # Per-node
        self.max_pkts_sent_this_cycle = 0
        self.max_pkts_received_this_cycle = 0
        self.max_pkts_dropped_this_cycle = 0
        self.max_node_memory_usage_this_cycle = 0
        self.max_current_q_len = 0


    def integrate_node_stats(self, nodestats:NodeDiagnostics):
        # Network-wide
        self.total_pkts_sent += nodestats.num_pkts_sent_this_cycle
        self.total_pkts_sent_this_cycle += nodestats.num_pkts_sent_this_cycle
        self.total_pkts_received += nodestats.num_pkts_sent_this_cycle
        self.total_pkts_received_this_cycle += nodestats.num_pkts_received_this_cycle
        self.total_pkts_dropped += nodestats.num_pkts_dropped_this_cycle
        self.total_pkts_dropped_this_cycle += nodestats.num_pkts_dropped_this_cycle
        self.total_pkts_queued += nodestats.current_q_len
        self.max_node_memory_usage_this_cycle = max(self.max_node_memory_usage_this_cycle, nodestats.total_cycle_mem)
        self.max_node_memory_usage = max(self.max_node_memory_usage, nodestats.max_mem)
        self.correctly_routed_pkts += nodestats.correctly_routed_pkts_this_cycle

        # Per-node
        if self.max_total_pkts_sent < nodestats.num_pkts_sent:
            self.max_total_pkts_sent = nodestats.num_pkts_sent
        if self.max_pkts_sent_this_cycle < nodestats.num_pkts_sent_this_cycle:
            self.max_pkts_sent_this_cycle = nodestats.num_pkts_sent_this_cycle
        
        if self.max_total_pkts_received < nodestats.num_pkts_received:
            self.max_total_pkts_received = nodestats.num_pkts_received
        if self.max_pkts_received_this_cycle < nodestats.num_pkts_received_this_cycle:
            self.max_pkts_received_this_cycle = nodestats.num_pkts_received_this_cycle

        if self.max_total_pkts_dropped < nodestats.num_pkts_dropped:
            self.max_total_pkts_dropped = nodestats.num_pkts_dropped
        if self.max_pkts_dropped_this_cycle < nodestats.num_pkts_dropped_this_cycle:
            self.max_pkts_dropped_this_cycle = nodestats.num_pkts_dropped_this_cycle

        if self.max_current_q_len < nodestats.current_q_len:
            self.max_current_q_len = nodestats.current_q_len
        if self.max_highest_q_len < nodestats.highest_q_len:
            self.max_highest_q_len = nodestats.highest_q_len


    def __str__(self):
        with io.StringIO() as sio:
            sio.write(
                '\n'.join([
                    "Network-Wide Statistics",
                    "-"*60,
                    f"Total Pkts Sent: {self.total_pkts_sent}",
                    f"Pkts Sent This Cycle: {self.total_pkts_sent_this_cycle}",
                    f"Total Pkts Received: {self.total_pkts_received}",
                    f"Pkts Received This Cycle: {self.total_pkts_received_this_cycle}",
                    f"Total Pkts Dropped: {self.total_pkts_dropped}",
                    f"Pkts Dropped This Cycle: {self.total_pkts_dropped_this_cycle}",
                    f"Packets Correctly Routed: {self.correctly_routed_pkts}",
                    f"Total Pkts in Queue: {self.total_pkts_queued}",
                    "-"*60,
                    "Per-Node Statistics",
                    "-"*60,
                    f"Max. Pkts Sent: {self.max_total_pkts_sent}",
                    f"Max. Pkts Sent This Cycle: {self.max_pkts_sent_this_cycle}",
                    f"Max. Pkts Received: {self.max_total_pkts_received}",
                    f"Max. Pkts Received This Cycle: {self.max_pkts_received_this_cycle}",
                    f"Max. Pkts Dropped: {self.max_total_pkts_dropped}",
                    f"Max. Pkts Dropped This Cycle: {self.max_pkts_dropped_this_cycle}",
                    f"Max. Current Queue Length: {self.max_current_q_len}",
                    f"Max. Node Memory Usage: {self.max_node_memory_usage}",
                    f"Max. Node Memory Usage This Cycle: {self.max_node_memory_usage_this_cycle}",
                    f"Highest Recorded Queue Length: {self.max_highest_q_len}",
                ])
            )
            return sio.getvalue()