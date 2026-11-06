import time
from collections import defaultdict
from typing import Dict, Any, Optional

class FlowKey:
    def __init__(self, src_ip: str, dst_ip: str, src_port: int, dst_port: int, protocol: str):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.src_port = src_port
        self.dst_port = dst_port
        self.protocol = protocol

    def to_tuple(self):
        return (self.src_ip, self.dst_ip, self.src_port, self.dst_port, self.protocol)

    def to_bi_tuple(self):
        # Định danh luồng song phương (Bi-directional flow)
        if (self.src_ip, self.src_port) <= (self.dst_ip, self.dst_port):
            return (self.src_ip, self.dst_ip, self.src_port, self.dst_port, self.protocol)
        return (self.dst_ip, self.src_ip, self.dst_port, self.src_port, self.protocol)

    def __hash__(self):
        return hash(self.to_bi_tuple())

    def __eq__(self, other):
        return self.to_bi_tuple() == other.to_bi_tuple()

    def __repr__(self):
        return f"{self.src_ip}:{self.src_port} <-> {self.dst_ip}:{self.dst_port} ({self.protocol})"

class FlowRecord:
    def __init__(self, flow_key: FlowKey, first_packet_time: float):
        self.key = flow_key
        self.start_time = first_packet_time
        self.last_time = first_packet_time
        self.fwd_packets = 0
        self.bwd_packets = 0
        self.fwd_bytes = 0
        self.bwd_bytes = 0
        self.packets = []
        self.is_finished = False

    def add_packet(self, pkt, timestamp: float, is_forward: bool = True):
        self.last_time = timestamp
        pkt_len = len(pkt)
        if is_forward:
            self.fwd_packets += 1
            self.fwd_bytes += pkt_len
        else:
            self.bwd_packets += 1
            self.bwd_bytes += pkt_len
        self.packets.append(pkt)

    @property
    def duration(self) -> float:
        return max(0.0, self.last_time - self.start_time)

    @property
    def total_packets(self) -> int:
        return self.fwd_packets + self.bwd_packets

    @property
    def total_bytes(self) -> int:
        return self.fwd_bytes + self.bwd_bytes

class FlowAggregator:
    """
    Bộ gom Packet thành Flow mạng chuẩn xác (Packet-to-Flow Aggregator)
    Hỗ trợ quản lý vòng đời luồng mạng, timeout và phát hiện kết thúc (FIN/RST).
    """
    def __init__(self, active_timeout: float = 60.0, idle_timeout: float = 15.0):
        self.active_timeout = active_timeout
        self.idle_timeout = idle_timeout
        self.active_flows: Dict[FlowKey, FlowRecord] = {}

    def process_packet(self, pkt) -> Optional[FlowRecord]:
        try:
            from scapy.layers.inet import IP, TCP, UDP
            if not pkt.haslayer(IP):
                return None

            src_ip = pkt[IP].src
            dst_ip = pkt[IP].dst
            proto = "TCP" if pkt.haslayer(TCP) else ("UDP" if pkt.haslayer(UDP) else "OTHER")
            src_port = pkt[TCP].sport if pkt.haslayer(TCP) else (pkt[UDP].sport if pkt.haslayer(UDP) else 0)
            dst_port = pkt[TCP].dport if pkt.haslayer(TCP) else (pkt[UDP].dport if pkt.haslayer(UDP) else 0)

            key = FlowKey(src_ip, dst_ip, src_port, dst_port, proto)
            timestamp = float(getattr(pkt, "time", time.time()))

            if key not in self.active_flows:
                flow = FlowRecord(key, timestamp)
                self.active_flows[key] = flow
            else:
                flow = self.active_flows[key]

            is_fwd = (src_ip == key.src_ip and src_port == key.src_port)
            flow.add_packet(pkt, timestamp, is_forward=is_fwd)

            # Kiểm tra cờ FIN hoặc RST để kết thúc flow TCP
            if pkt.haslayer(TCP):
                flags = pkt[TCP].flags
                if flags.F or flags.R:
                    flow.is_finished = True
                    return self.active_flows.pop(key)

            # Kiểm tra active timeout
            if flow.duration >= self.active_timeout:
                flow.is_finished = True
                return self.active_flows.pop(key)

            return None
        except Exception:
            return None

    def flush_expired_flows(self, current_time: Optional[float] = None) -> list[FlowRecord]:
        now = current_time or time.time()
        expired = []
        for key, flow in list(self.active_flows.items()):
            if (now - flow.last_time) >= self.idle_timeout or (flow.duration >= self.active_timeout):
                flow.is_finished = True
                expired.append(flow)
                del self.active_flows[key]
        return expired

