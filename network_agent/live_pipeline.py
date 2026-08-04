import os
import time
import pandas as pd
import numpy as np
import json 
import logging
import threading
import queue
import requests
import signal # BỔ SUNG: Bắt tín hiệu từ Backend
import sys    # BỔ SUNG: Để thoát tiến trình an toàn
from datetime import datetime
from collections import Counter
from scapy.utils import PcapReader

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import sniff, wrpcap, DNSQR
from scapy.layers.tls.all import TLS_Ext_ServerName 
from ai_core import load_ai_model, features_to_tensor, predict
from cicflowmeter.sniffer import create_sniffer

pcap_queue = queue.Queue()
is_running = True
print_lock = threading.Lock() 

## ========================================================
# TẠO FOLDER LƯU TRỮ DỮ LIỆU ĐÁNH GIÁ (DATASETS)
# ========================================================
DATASET_DIR = "csv" # Đổi tên thư mục thành 'csv'
if not os.path.exists(DATASET_DIR):
    os.makedirs(DATASET_DIR)
    
# THÊM GIỜ-PHÚT-GIÂY VÀO TÊN FILE
# Vì mỗi lần bấm "KÍCH HOẠT LẮNG NGHE" trên Web, Backend sẽ gọi lại script này,
# nên thời gian sẽ được làm mới, tạo ra một file CSV độc lập cho mỗi phiên.
current_session_time = datetime.now().strftime("%Y%m%d_%H%M%S")
CSV_OUT_PATH = os.path.join(DATASET_DIR, f"network_test_dataset_{current_session_time}.csv")

KAGGLE_COLUMNS = [
    'dst_port', 'protocol', 'flow_duration', 'tot_fwd_pkts', 'tot_bwd_pkts', 'totlen_fwd_pkts', 'totlen_bwd_pkts', 
    'fwd_pkt_len_max', 'fwd_pkt_len_min', 'fwd_pkt_len_mean', 'fwd_pkt_len_std', 
    'bwd_pkt_len_max', 'bwd_pkt_len_min', 'bwd_pkt_len_mean', 'bwd_pkt_len_std', 
    'flow_byts_s', 'flow_pkts_s', 'flow_iat_mean', 'flow_iat_std', 'flow_iat_max', 'flow_iat_min', 
    'fwd_iat_tot', 'fwd_iat_mean', 'fwd_iat_std', 'fwd_iat_max', 'fwd_iat_min', 
    'bwd_iat_tot', 'bwd_iat_mean', 'bwd_iat_std', 'bwd_iat_max', 'bwd_iat_min', 
    'fwd_psh_flags', 'bwd_psh_flags', 'fwd_urg_flags', 'bwd_urg_flags', 
    'fwd_header_len', 'bwd_header_len', 'fwd_pkts_s', 'bwd_pkts_s', 
    'pkt_len_min', 'pkt_len_max', 'pkt_len_mean', 'pkt_len_std', 'pkt_len_var', 
    'fin_flag_cnt', 'syn_flag_cnt', 'rst_flag_cnt', 'psh_flag_cnt', 'ack_flag_cnt', 
    'urg_flag_cnt', 'cwr_flag_count', 'ece_flag_cnt', 'down_up_ratio', 'pkt_size_avg', 
    'fwd_seg_size_avg', 'bwd_seg_size_avg', 'fwd_header_len', 
    'fwd_byts_b_avg', 'fwd_pkts_b_avg', 'fwd_blk_rate_avg', 
    'bwd_byts_b_avg', 'bwd_pkts_b_avg', 'bwd_blk_rate_avg', 
    'subflow_fwd_pkts', 'subflow_fwd_byts', 'subflow_bwd_pkts', 'subflow_bwd_byts', 
    'init_fwd_win_byts', 'init_bwd_win_byts', 'fwd_act_data_pkts', 'fwd_seg_size_min', 
    'active_mean', 'active_std', 'active_max', 'active_min', 
    'idle_mean', 'idle_std', 'idle_max', 'idle_min'
]

BACKEND_URL = "http://localhost:8000/api/v1/save-log"

def safe_print(message):
    with print_lock:
        print(message)

# ========================================================
# HÀM XỬ LÝ TÍN HIỆU TẮT AN TOÀN TỪ BACKEND HOẶC BÀN PHÍM
# ========================================================
def shutdown_handler(signum, frame):
    global is_running
    signame = signal.Signals(signum).name
    safe_print(f"\n[HỆ THỐNG] Đã nhận lệnh tắt ({signame}). Đang dọn dẹp các luồng...")
    is_running = False
    
# Gắn cờ bắt tín hiệu. SIGINT = Bấm Ctrl+C. SIGTERM = Lệnh tắt ngầm từ Web (Backend).
signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)


def capture_traffic_loop(duration=10):
    global is_running
    while is_running:
        try:
            safe_print(f"\n[Luồng Thu Thập] Đang nghe lén mạng trong {duration} giây...")
            packets = sniff(timeout=duration, filter="tcp or udp")
            
            # Kiểm tra lại is_running vì trong lúc sniff có thể đã bị ngắt
            if not is_running: break 
            
            pkt_count = len(packets)
            if pkt_count > 0:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pcap_filename = f"traffic_{timestamp}.pcap"
                
                safe_print(f"-> [Luồng Thu Thập] Đã bắt được {pkt_count} gói tin. Chuyển sang hàng đợi...")
                wrpcap(pcap_filename, packets)
                pcap_queue.put((pcap_filename, pkt_count)) 
            else:
                safe_print("-> [Luồng Thu Thập] Không có luồng giao tiếp nào.")
        except Exception as e:
            if is_running: safe_print(f"Lỗi ở luồng bắt gói tin: {e}")

def process_data_loop(model):
    global is_running
    while is_running:
        try:
            queue_item = pcap_queue.get(timeout=3)
            pcap_filename, pkt_count = queue_item
            csv_filename = pcap_filename.replace('.pcap', '.csv')
            
            abs_pcap = os.path.abspath(pcap_filename)
            abs_csv_out = os.path.abspath(csv_filename)
            
            try:
                sniffer_obj, session = create_sniffer(
                    input_file=abs_pcap, input_interface=None, output_mode="csv",
                    output=abs_csv_out, input_directory=None, fields=None, verbose=False
                )
                sniffer_obj.start()
                sniffer_obj.join()
                
                if hasattr(session, '_gc_stop'):
                    session._gc_stop.set()
                    session._gc_thread.join(timeout=2.0)
                session.flush_flows()
                cic_success = True
            except Exception as e:
                safe_print(f"-> [Lỗi Lõi CIC] Bỏ qua file do lỗi dịch: {e}")
                cic_success = False
            
            if cic_success and os.path.exists(abs_csv_out):
                prediction_result = analyze_with_ai(model, abs_csv_out)
                visited_websites = extract_domains(abs_pcap)
                
                log_data = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "ai_prediction": prediction_result,
                    "packet_count": pkt_count,
                    "websites": visited_websites
                }
                
                safe_print("\n" + "="*60)
                safe_print(f"🟢 [BACKEND READY] DỮ LIỆU JSON (GÓI {pkt_count} PACKETS):")
                safe_print(json.dumps(log_data, indent=4, ensure_ascii=False))
                safe_print("="*60)

                try:
                    requests.post(BACKEND_URL, json=log_data, timeout=3)
                except Exception as err:
                    safe_print(f"-> [Cảnh báo Web] Chưa thể đẩy dữ liệu lên Backend: {err}")
            
            if os.path.exists(abs_pcap): os.remove(abs_pcap)
            if os.path.exists(abs_csv_out): os.remove(abs_csv_out)
            
            pcap_queue.task_done()
            
        except queue.Empty:
            continue 
        except Exception as e:
            if is_running: safe_print(f"-> [Cảnh báo Luồng Xử Lý] Xảy ra lỗi ngoài ý muốn: {e}")

def analyze_with_ai(model, csv_filename):
    try:
        df = pd.read_csv(csv_filename)
        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        if df.empty: return "Unknown"
        
        df_ordered = pd.DataFrame()
        for col in KAGGLE_COLUMNS:
            if col in df.columns:
                df_ordered[col] = df[col]
            else:
                df_ordered[col] = 0.0
                
        df_numeric = df_ordered.astype(float)
        predictions = []
        valid_features = []
        
        for index, row in df_numeric.iterrows():
            try:
                tensor_data = features_to_tensor(row.tolist())
                result = predict(model, tensor_data)
                predictions.append(result)
                valid_features.append(row.tolist())
            except Exception: continue
                
        if not predictions: return "Unknown"
        
        export_df = pd.DataFrame(valid_features, columns=df_ordered.columns)
        export_df['AI_Prediction'] = predictions
        
        write_header = not os.path.exists(CSV_OUT_PATH)
        export_df.to_csv(CSV_OUT_PATH, mode='a', header=write_header, index=False)
        safe_print(f"💾 [DATASET] Đã trích xuất và lưu {len(predictions)} luồng vào {CSV_OUT_PATH}")
        
        label_counts = Counter(predictions)
        most_common_label = label_counts.most_common(1)[0][0]
        
        safe_print(f"🤖 [AI] Hành vi chính: {most_common_label} (Chi tiết: {dict(label_counts)})")
        return most_common_label
    except Exception as e:
        safe_print(f"[AI] Lỗi phân tích: {e}")
        return "Error"

def extract_domains(pcap_filename):
    domains = set() 
    BLACKLIST_KEYWORDS = [
        'doubleclick', 'syndication', 'analytics', 'clarity.ms', 'adsafe', 
        'adnxs.com', 'criteo.com', 'gstatic', 'cloudflareinsights', 
        'tracking', 'telemetry', 'cdn', 'ggpht.com', 'adtraffic', 'adster'
    ]

    try:
        with PcapReader(pcap_filename) as pcap_reader:
            for pkt in pcap_reader:
                domain_name = None
                if pkt.haslayer(DNSQR):
                    domain_name = pkt[DNSQR].qname.decode('utf-8').strip('.')
                elif pkt.haslayer(TLS_Ext_ServerName):
                    try:
                        server_names = pkt[TLS_Ext_ServerName].servernames
                        if server_names: 
                            domain_name = server_names[0].servername.decode('utf-8')
                    except: pass
                
                if domain_name:
                    domain_name = domain_name.lower()
                    if domain_name.endswith('.local') or domain_name.endswith('.arpa'):
                        continue
                    
                    is_junk = any(junk in domain_name for junk in BLACKLIST_KEYWORDS)
                    if not is_junk:
                        domains.add(domain_name)
    except: pass
    
    return list(domains)

def main():
    global is_running
    os.system('clear' if os.name == 'posix' else 'cls')
    print("🚀 KHỞI ĐỘNG HỆ THỐNG GIÁM SÁT MẠNG TỰ ĐỘNG (FINAL VERSION) 🚀")
    model = load_ai_model('model_final_Application_Label.pth')
    
    capture_thread = threading.Thread(target=capture_traffic_loop, args=(10,))
    capture_thread.daemon = True 
    process_thread = threading.Thread(target=process_data_loop, args=(model,))
    process_thread.daemon = True
    
    capture_thread.start()
    process_thread.start()
    
    # Vòng lặp chính chờ đợi cho đến khi is_running = False (Do Signal đổi)
    while is_running: 
        time.sleep(1)
        
    print("\n[HỆ THỐNG] Đang chờ hoàn tất các luồng xử lý cuối cùng...")
    capture_thread.join(timeout=2)
    process_thread.join(timeout=2)
    print("Đã thoát an toàn!")
    sys.exit(0)

if __name__ == "__main__":
    main()