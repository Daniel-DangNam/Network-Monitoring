import os
from typing import Dict, Any

class PcapService:
    @staticmethod
    def parse_pcap_file(file_path: str) -> Dict[str, Any]:
        """Bóc tách thông tin cơ bản từ file PCAP"""
        try:
            from scapy.all import rdpcap, IP, TCP, UDP
            file_size = os.path.getsize(file_path)
            packets = rdpcap(file_path)
            total_packets = len(packets)
            
            flows = set()
            src_ip = "N/A"
            dst_ip = "N/A"
            protocol = "Other"

            for pkt in packets:
                if pkt.haslayer(IP):
                    if src_ip == "N/A":
                        src_ip = pkt[IP].src
                        dst_ip = pkt[IP].dst
                        if pkt.haslayer(TCP):
                            protocol = "TCP"
                        elif pkt.haslayer(UDP):
                            protocol = "UDP"

                    # 5-tuple gom flow
                    sport = pkt[TCP].sport if pkt.haslayer(TCP) else (pkt[UDP].sport if pkt.haslayer(UDP) else 0)
                    dport = pkt[TCP].dport if pkt.haslayer(TCP) else (pkt[UDP].dport if pkt.haslayer(UDP) else 0)
                    proto = "TCP" if pkt.haslayer(TCP) else ("UDP" if pkt.haslayer(UDP) else "OTHER")
                    flows.add((pkt[IP].src, pkt[IP].dst, sport, dport, proto))

            return {
                "file_size_bytes": file_size,
                "total_packets": total_packets,
                "total_flows": len(flows),
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "protocol": protocol,
                "predicted_labels": []
            }
        except Exception as e:
            return {
                "file_size_bytes": 0,
                "total_packets": 0,
                "total_flows": 0,
                "src_ip": "N/A",
                "dst_ip": "N/A",
                "protocol": "N/A",
                "predicted_labels": [],
                "error": str(e)
            }

pcap_service = PcapService()

