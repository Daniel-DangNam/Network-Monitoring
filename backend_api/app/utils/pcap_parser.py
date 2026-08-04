import os
from scapy.all import rdpcap, IP, TCP, UDP

def extract_pcap_info(file_path: str) -> dict:
    """
    Đọc file PCAP bằng Scapy và trích xuất các thông tin cơ bản
    """
    try:
        # Lấy kích thước file (bytes)
        file_size = os.path.getsize(file_path)
        
        # Đọc danh sách gói tin trong file
        packets = rdpcap(file_path)
        total_packets = len(packets)
        
        src_ip = "N/A"
        dst_ip = "N/A"
        protocol = "Other"
        
        # Lấy thông tin từ gói tin IP đầu tiên tìm thấy
        for pkt in packets:
            if pkt.haslayer(IP):
                src_ip = pkt[IP].src
                dst_ip = pkt[IP].dst
                if pkt.haslayer(TCP):
                    protocol = "TCP"
                elif pkt.haslayer(UDP):
                    protocol = "UDP"
                break

        return {
            "file_size_bytes": file_size,
            "total_packets": total_packets,
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "protocol": protocol
        }
    except Exception as e:
        return {
            "error": f"Lỗi bóc tách file PCAP: {str(e)}",
            "file_size_bytes": 0,
            "total_packets": 0,
            "src_ip": "N/A",
            "dst_ip": "N/A",
            "protocol": "N/A"
        }