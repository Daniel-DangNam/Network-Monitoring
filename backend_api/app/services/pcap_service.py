import os
import sys
import tempfile
from collections import Counter
from typing import Dict, Any, List


class PcapService:
    _cached_model = None

    @classmethod
    def _get_agent_dir(cls) -> str:
        backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        return os.path.join(backend_root, "network_agent")

    @classmethod
    def _get_ai_model(cls):
        if cls._cached_model is not None:
            return cls._cached_model
        agent_dir = cls._get_agent_dir()
        if agent_dir not in sys.path:
            sys.path.insert(0, agent_dir)
        from ai_core import load_ai_model
        model_path = os.path.join(agent_dir, "model_final_Application_Label.pth")
        if not os.path.exists(model_path):
            model_path = os.path.join(agent_dir, "models", "model_final_Application_Label.pth")
        cls._cached_model = load_ai_model(model_path)
        return cls._cached_model

    @classmethod
    def parse_pcap_file(cls, file_path: str) -> Dict[str, Any]:
        """Bóc tách thông tin 5-Tuple, tên miền và chạy AI-Fusion phân loại tệp PCAP."""
        try:
            from scapy.all import rdpcap, IP, TCP, UDP

            agent_dir = cls._get_agent_dir()
            if agent_dir not in sys.path:
                sys.path.insert(0, agent_dir)

            file_size = os.path.getsize(file_path)
            packets = rdpcap(file_path)
            total_packets = len(packets)

            flows = set()
            src_ip = "N/A"
            dst_ip = "N/A"
            protocol = "Other"
            client_ips: List[str] = []
            seen_clients = set()

            for pkt in packets:
                if pkt.haslayer(IP):
                    p_src = pkt[IP].src
                    p_dst = pkt[IP].dst
                    if src_ip == "N/A":
                        src_ip = p_src
                        dst_ip = p_dst
                        if pkt.haslayer(TCP):
                            protocol = "TCP"
                        elif pkt.haslayer(UDP):
                            protocol = "UDP"

                    if p_src not in seen_clients and not p_src.startswith(("127.", "224.", "239.", "255.")):
                        seen_clients.add(p_src)
                        if p_src.startswith(("10.", "192.168.", "172.")):
                            client_ips.append(p_src)

                    sport = pkt[TCP].sport if pkt.haslayer(TCP) else (pkt[UDP].sport if pkt.haslayer(UDP) else 0)
                    dport = pkt[TCP].dport if pkt.haslayer(TCP) else (pkt[UDP].dport if pkt.haslayer(UDP) else 0)
                    proto = "TCP" if pkt.haslayer(TCP) else ("UDP" if pkt.haslayer(UDP) else "OTHER")
                    flows.add((p_src, p_dst, sport, dport, proto))

            # 1. Trích xuất tên miền TLS SNI & DNS
            websites: List[str] = []
            try:
                from live_pipeline import extract_domains_from_packets
                websites = extract_domains_from_packets(packets)
            except Exception:
                websites = []

            # 2. Chạy CICFlowMeter + AI-Fusion nếu có đủ luồng hợp lệ
            predicted_labels: List[str] = []
            primary_domain = websites[0] if websites else "Unknown"

            fd, tmp_csv = tempfile.mkstemp(suffix=".csv")
            os.close(fd)
            try:
                from cicflowmeter.sniffer import create_sniffer
                import pandas as pd
                import numpy as np
                from ai_core import features_to_tensor, parallel_fusion_predict
                from live_pipeline import KAGGLE_COLUMNS

                sniffer_obj, session = create_sniffer(
                    input_file=os.path.abspath(file_path),
                    input_interface=None,
                    output_mode="csv",
                    output=tmp_csv,
                    input_directory=None,
                    fields=None,
                    verbose=False,
                )
                sniffer_obj.start()
                sniffer_obj.join()
                if hasattr(session, "_gc_stop"):
                    session._gc_stop.set()
                    session._gc_thread.join(timeout=2.0)
                session.flush_flows()

                if os.path.exists(tmp_csv) and os.path.getsize(tmp_csv) > 0:
                    df = pd.read_csv(tmp_csv).replace([np.inf, -np.inf], np.nan).dropna()
                    if not df.empty:
                        model = cls._get_ai_model()
                        df_ordered = pd.DataFrame()
                        for col in KAGGLE_COLUMNS:
                            df_ordered[col] = df[col] if col in df.columns else 0.0
                        for _, row in df_ordered.astype(float).iterrows():
                            proto_val = int(row["protocol"]) if "protocol" in row else 6
                            dport_val = int(row["dst_port"]) if "dst_port" in row else 0
                            tensor_data = features_to_tensor(row.tolist())
                            label = parallel_fusion_predict(model, tensor_data, primary_domain, proto_val, dport_val)
                            if label != "IGNORED":
                                predicted_labels.append(label)
            except Exception:
                pass
            finally:
                if os.path.exists(tmp_csv):
                    os.remove(tmp_csv)

            # Fallback sang Rule-based nếu file PCAP quá nhỏ (chưa đóng đủ flow CIC) nhưng có tên miền
            if not predicted_labels and primary_domain != "Unknown":
                try:
                    from ai_core import SNI_RULES_ADVANCED
                    domain_lower = primary_domain.lower()
                    for key, label in SNI_RULES_ADVANCED.items():
                        if key in domain_lower:
                            predicted_labels.append(label)
                            break
                except Exception:
                    pass

            summary_label = Counter(predicted_labels).most_common(1)[0][0] if predicted_labels else "Unknown"
            unique_labels = list(dict.fromkeys(predicted_labels))

            return {
                "file_size_bytes": file_size,
                "total_packets": total_packets,
                "total_flows": len(flows),
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "protocol": protocol,
                "summary_label": summary_label,
                "predicted_labels": unique_labels,
                "websites": websites,
                "client_ips": client_ips[:10],
            }
        except Exception as e:
            return {
                "file_size_bytes": 0,
                "total_packets": 0,
                "total_flows": 0,
                "src_ip": "N/A",
                "dst_ip": "N/A",
                "protocol": "N/A",
                "summary_label": "Unknown",
                "predicted_labels": [],
                "websites": [],
                "client_ips": [],
                "error": str(e),
            }


pcap_service = PcapService()
