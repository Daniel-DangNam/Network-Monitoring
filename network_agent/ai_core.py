import torch
import torch.nn as nn
import torchvision.models as models
import numpy as np

# Danh sách 11 nhãn theo đúng thứ tự huấn luyện (0-10)
CLASS_NAMES = [
    'Streaming', 'VPN-VoIP', 'VPN-chat', 'VPN-email', 'VPN-file_transfer',
    'VPN-p2p', 'VPN-streaming', 'VoIP', 'chat', 'email', 'file_transfer'
]

# --- BỘ TỪ ĐIỂN RULE-BASED THỰC CHIẾN (MỞ RỘNG) ---
SNI_RULES_ADVANCED = {
    # 1. EMAIL
    'mail.google.com': 'email',
    'mail-attachment.googleusercontent.com': 'email',
    'inbox.google.com': 'email',
    'outlook.live.com': 'email',
    'outlook.office.com': 'email',
    'outlook.office365.com': 'email',
    'smtp': 'email',
    'imap': 'email',
    'pop3': 'email',

    # 2. STREAMING
    'googlevideo.com': 'Streaming',
    'youtube.com': 'Streaming',
    'ytimg.com': 'Streaming',
    'video.xx.fbcdn.net': 'Streaming',
    'nflxvideo.net': 'Streaming',
    'netflix.com': 'Streaming',
    'vimeocdn.com': 'Streaming',
    'ttvnw.net': 'Streaming',
    
    # 3. FILE TRANSFER
    'drive.google.com': 'file_transfer',
    'docs.google.com': 'file_transfer',
    'drive-thirdparty.googleusercontent.com': 'file_transfer',
    'clients6.google.com': 'file_transfer',
    'dropbox.com': 'file_transfer',
    'onedrive.live.com': 'file_transfer',
    'fbsbx.com': 'file_transfer',
    'sharepoint.com': 'file_transfer',
    'mediafire.com': 'file_transfer',
    'mega.nz': 'file_transfer',

    # 4. P2P TRACKERS
    'opentrackr': 'p2p',
    'openbittorrent': 'p2p',
    'tracker': 'p2p',
    'torrent': 'p2p',
    'announce': 'p2p',
    'dht.transmissionbt.com': 'p2p',
}

def load_ai_model(model_path):
    print("[AI] Đang nạp cấu trúc ResNet-18 tùy chỉnh...")
    model = models.resnet18(weights=None)
    
    # Ép khung kiến trúc khớp với file .pth
    model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
    num_ftrs = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(num_ftrs, 11)
    )
    
    print("[AI] Đang tải trọng số mô hình...")
    checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
    
    if 'model_state_dict' in checkpoint:
        model.load_state_dict(checkpoint['model_state_dict'])
    else:
        model.load_state_dict(checkpoint)
    
    model.eval()
    print("[AI] Lõi AI đã sẵn sàng!")
    return model

def features_to_tensor(features_list):
    # Tự động đệm số 0 cho đủ 81 phần tử (9x9)
    features_81 = list(features_list)
    
    if len(features_81) < 81:
        padding_needed = 81 - len(features_81)
        features_81.extend([0.0] * padding_needed)
    elif len(features_81) > 81:
        features_81 = features_81[:81]
    
    arr = np.array(features_81, dtype=np.float32)
    
    # Chuẩn hóa Min-Max cục bộ
    arr_min, arr_max = np.min(arr), np.max(arr)
    if arr_max - arr_min != 0:
        arr_normalized = (arr - arr_min) / (arr_max - arr_min)
    else:
        arr_normalized = arr - arr_min
        
    # Nặn thành ma trận vuông 9x9 và chồng lên 3 kênh màu RGB
    image_9x9 = arr_normalized.reshape(9, 9)
    image_rgb = np.stack([image_9x9, image_9x9, image_9x9], axis=0)
    
    # Thêm chiều batch_size và chuyển sang Tensor
    tensor_input = torch.tensor(np.expand_dims(image_rgb, axis=0), dtype=torch.float32)
    return tensor_input

def predict(model, tensor_input):
    with torch.no_grad():
        output = model(tensor_input)
        idx = torch.argmax(output, dim=1).item()
        return CLASS_NAMES[idx]

def hybrid_predict_advanced(model, tensor_input, sni_domain, protocol, dst_port=0):
    """
    Hệ thống phân loại Lai (Hybrid): Giao thức (Protocol) + Tên miền (SNI) + Học sâu (AI).
    """
    domain_lower = str(sni_domain).lower()
    
    # ==========================================
    # BƯỚC 1: RULE-BASED CHO KẾT NỐI KHÔNG BẬT VPN (CÓ TÊN MIỀN RÕ)
    # ==========================================
    
    # 1.1 Xử lý ưu tiên cho các Ứng dụng Thoại / Họp / Nhắn tin theo Giao thức
    chat_voip_apps = [
        'zalo', 'zadn.vn', 'zalocdn', 'telegram', 't.me', 'messenger',
        'meet.google', 'hangouts', 'teams', 'discord', 'zoom', 'skype', 'webrtc', 'cloudapp.azure.com'
    ]
    if any(app in domain_lower for app in chat_voip_apps):
        if protocol == 17:  # UDP -> Truyền tải âm thanh/video thoại thời gian thực
            return "VoIP"
        else:               # TCP -> Nhắn tin văn bản, kết nối báo hiệu
            return "chat"
            
    if 'tiktok' in domain_lower:
        if protocol == 17:
            return "Streaming"
        else:
            return "chat"

    # 1.2 Xử lý dải máy chủ động của Google (Đảm bảo Test 2 và Test 3)
    if '.googleusercontent.com' in domain_lower:
        subdomain = domain_lower.split('.googleusercontent.com')[0]
        # Nếu có tiền tố ci (máy chủ ảnh/icon của mail) hoặc mail-attachment -> Email
        if subdomain.startswith('ci') or 'mail' in subdomain or subdomain.startswith('lh'):
            return 'email'
        # Nếu là máy chủ download Drive/Docs/Storage -> File Transfer
        elif 'drive' in subdomain:
            return 'file_transfer'

    # 1.3 Quét qua bộ từ điển CDN / Subdomain cố định
    for key, label in SNI_RULES_ADVANCED.items():
        if key in domain_lower:
            return label

    # 1.4 Bổ sung cho VoIP khi không bắt được tên miền nhưng chạy UDP trên cổng đặc thù (3478 WebRTC STUN)
    if protocol == 17 and (dst_port == 3478 or dst_port > 10000):
        return "VoIP"

    # ==========================================
    # BƯỚC 2: GIAO CHO AI DỰ ĐOÁN
    # (Áp dụng khi bật VPN hoặc khi rule-based không xác định được)
    # ==========================================
    with torch.no_grad():
        output = model(tensor_input)
        idx = torch.argmax(output, dim=1).item()
        pred = CLASS_NAMES[idx]

    # ==========================================
    # BƯỚC 3: BỌC LÓT (ANTI-VPN BIAS)
    # Nếu hệ thống bắt được tên miền (tức là KHÔNG BẬT VPN),
    # nhưng AI lỡ tay gán tiền tố VPN- thì ta gọt bỏ đi.
    # ==========================================
    if domain_lower not in ['', 'none', 'unknown', 'nan']:
        if pred.startswith('VPN-'):
            return pred.replace('VPN-', '') # Ví dụ 'VPN-file_transfer' -> 'file_transfer'
        return pred

    # Nếu đang bật VPN thực sự (không có domain), trả thẳng kết quả dự đoán của AI.
    return pred