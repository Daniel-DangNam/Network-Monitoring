import argparse
import os
import sys

# Đảm bảo đường dẫn import
agent_dir = os.path.dirname(os.path.abspath(__file__))
if agent_dir not in sys.path:
    sys.path.insert(0, agent_dir)

from core.config import config
from core.flow_aggregator import FlowAggregator

def run_live():
    print("[Network Agent] Bắt đầu chế độ Bắt gói tin trực tiếp (Live Sniffing)...")
    # Chạy pipeline thời gian thực
    import live_pipeline
    live_pipeline.main()

def run_pcap(pcap_path):
    print(f"[Network Agent] Bắt đầu phân tích tệp PCAP: {pcap_path}")
    from scapy.all import rdpcap
    aggregator = FlowAggregator()
    packets = rdpcap(pcap_path)
    print(f"[Network Agent] Tổng số gói tin đã nạp: {len(packets)}")
    
    for pkt in packets:
        aggregator.process_packet(pkt)
    
    expired = aggregator.flush_expired_flows()
    print(f"[Network Agent] Phân tách thành công: {len(expired)} luồng (Flows)")
    for i, flow in enumerate(expired[:10]):
        print(f"  Flow #{i+1}: {flow.key} | {flow.total_packets} pkts | {flow.total_bytes} bytes | {flow.duration:.2f}s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Network AI Monitoring Agent (DATN Edition)")
    parser.add_argument("--mode", choices=["live", "pcap"], default="live", help="Chế độ hoạt động")
    parser.add_argument("--file", type=str, default="", help="Đường dẫn tệp PCAP khi dùng mode pcap")
    args = parser.parse_args()

    if args.mode == "pcap":
        if not args.file or not os.path.exists(args.file):
            print(f"[Lỗi] Tệp PCAP không tồn tại: {args.file}")
            sys.exit(1)
        run_pcap(args.file)
    else:
        run_live()

