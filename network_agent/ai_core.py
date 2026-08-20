import torch
import torch.nn as nn
import torchvision.models as models
import numpy as np

# Danh sách 11 nhãn theo đúng thứ tự huấn luyện (0-10)
CLASS_NAMES = [
    'Streaming', 'VPN-VoIP', 'VPN-chat', 'VPN-email', 'VPN-file_transfer',
    'VPN-p2p', 'VPN-streaming', 'VoIP', 'chat', 'email', 'file_transfer'
]

# --- BỘ TỪ ĐIỂN RULE-BASED (DÀNH CHO LÚC KHÔNG BẬT VPN) ---
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

    # 4. P2P TRACKERS / SERVICES
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
    features_81 = list(features_list)
    
    if len(features_81) < 81:
        padding_needed = 81 - len(features_81)
        features_81.extend([0.0] * padding_needed)
    elif len(features_81) > 81:
        features_81 = features_81[:81]
    
    arr = np.array(features_81, dtype=np.float32)
    
    arr_min, arr_max = np.min(arr), np.max(arr)
    if arr_max - arr_min != 0:
        arr_normalized = (arr - arr_min) / (arr_max - arr_min)
    else:
        arr_normalized = arr - arr_min
        
    image_9x9 = arr_normalized.reshape(9, 9)
    image_rgb = np.stack([image_9x9, image_9x9, image_9x9], axis=0)
    tensor_input = torch.tensor(np.expand_dims(image_rgb, axis=0), dtype=torch.float32)
    return tensor_input

def predict(model, tensor_input):
    with torch.no_grad():
        output = model(tensor_input)
        idx = torch.argmax(output, dim=1).item()
        return CLASS_NAMES[idx]

def hybrid_predict_advanced(model, tensor_input, sni_domain, protocol, dst_port=0):
    domain_lower = str(sni_domain).lower()

    # ==========================================
    # BƯỚC 1: XỬ LÝ KHI KHÔNG BẬT VPN (CÓ DOMAIN)
    # ==========================================
    for key, label in SNI_RULES_ADVANCED.items():
        if key in domain_lower:
            return label

    # Nhận diện Chat & VoIP không bật VPN
    chat_voip_apps = [
        'zalo', 'zadn.vn', 'zalocdn', 'telegram', 't.me', 'messenger',
        'meet.google', 'hangouts', 'teams', 'discord', 'zoom'
    ]
    if any(app in domain_lower for app in chat_voip_apps):
        if protocol == 17:  
            return "VoIP"
        else:               
            return "chat"

    # ==========================================
    # BƯỚC 2: XỬ LÝ KHI BẬT VPN (ẨN DANH DOMAIN)
    # ==========================================
    # Để ResNet-18 tự do đưa ra quyết định dự đoán
    with torch.no_grad():
        output = model(tensor_input)
        idx = torch.argmax(output, dim=1).item()
        pred = CLASS_NAMES[idx]

    # Nếu domain trống (tức là đã bật VPN), đồng bộ tiền tố 'VPN-' cho đồng nhất kết quả
    if domain_lower in ['', 'none', 'unknown', 'nan']:
        if not pred.startswith('VPN-'):
            if pred == 'Streaming': return 'VPN-streaming'
            if pred == 'file_transfer': return 'VPN-file_transfer'
            if pred == 'chat': return 'VPN-chat'
            if pred == 'email': return 'VPN-email'
            if pred == 'VoIP': return 'VPN-VoIP'
            if pred == 'p2p': return 'VPN-p2p'
            return f"VPN-{pred}"
        return pred

    # Nếu không trúng rule nào mà có domain, cứ trả về dự đoán của AI
    return pred