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
    'dropbox.com': 'file_transfer',
    'onedrive.live.com': 'file_transfer',
    'fbsbx.com': 'file_transfer',
    'sharepoint.com': 'file_transfer',
    'mediafire.com': 'file_transfer',
    'mega.nz': 'file_transfer',
}

def load_ai_model(model_path):
    print("[AI] Đang nạp cấu trúc ResNet-18 (Chế độ Parallel Fusion)...")
    model = models.resnet18(weights=None)
    model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
    num_ftrs = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(num_ftrs, 11)
    )
    checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
    if 'model_state_dict' in checkpoint:
        model.load_state_dict(checkpoint['model_state_dict'])
    else:
        model.load_state_dict(checkpoint)
    model.eval()
    return model

def features_to_tensor(features_list):
    features_81 = list(features_list)
    if len(features_81) < 81:
        features_81.extend([0.0] * (81 - len(features_81)))
    elif len(features_81) > 81:
        features_81 = features_81[:81]
    
    arr = np.array(features_81, dtype=np.float32)
    arr = np.nan_to_num(arr, nan=0.0, posinf=1.0, neginf=0.0) # Khử lỗi tính toán
    
    arr_min, arr_max = np.min(arr), np.max(arr)
    if arr_max - arr_min != 0:
        arr_normalized = (arr - arr_min) / (arr_max - arr_min)
    else:
        arr_normalized = arr - arr_min
        
    image_9x9 = arr_normalized.reshape(9, 9)
    image_rgb = np.stack([image_9x9, image_9x9, image_9x9], axis=0)
    return torch.tensor(np.expand_dims(image_rgb, axis=0), dtype=torch.float32)

def parallel_fusion_predict(model, tensor_input, sni_domain, protocol, dst_port=0):
    """
    Hệ thống Dung hợp Quyết định (Decision-Level Fusion)
    Chạy song song Rule-Based và AI, sau đó Trọng tài phân xử.
    """
    domain_lower = str(sni_domain).lower().strip() if sni_domain else ""
    
    # ==========================================
    # BÁC SĨ 1: RULE-BASED (Khám bằng Tên miền)
    # ==========================================
    rule_pred = "UNKNOWN"
    if domain_lower not in ['', 'none', 'unknown', 'nan']:
        # Xử lý Cú lừa hệ sinh thái Google 
        if 'googleusercontent.com' in domain_lower:
            subdomain = domain_lower.split('.googleusercontent.com')[0]
            if subdomain.startswith('ci') or 'mail' in subdomain or subdomain.startswith('lh'):
                rule_pred = 'email'
            else:
                rule_pred = 'google_ecosystem'
                
        # ---> VÁ LỖI GOOGLE MEET VÀ HỌP TRỰC TUYẾN <---
        elif any(app in domain_lower for app in ['meet.google', 'zoom', 'teams', 'webex']):
            rule_pred = 'VoIP'
            
        # Ưu tiên các app có thể vừa Chat vừa Gọi điện (Zalo, Tele, Messenger)
        elif any(app in domain_lower for app in ['zalo', 'zadn.vn', 'telegram', 'messenger', 'discord', 'skype']):
            rule_pred = 'chat' # Mặc định là chat, chờ AI xác nhận xem có gọi thoại không
            if protocol == 17 or dst_port == 3478: 
                rule_pred = 'VoIP'
                
        # Quét từ điển cứng
        else:
            for key, label in SNI_RULES_ADVANCED.items():
                if key in domain_lower:
                    rule_pred = label
                    break

    # ==========================================
    # BÁC SĨ 2: AI RESNET-18 (Khám bằng Hành vi vật lý luồng)
    # ==========================================
    with torch.no_grad():
        output = model(tensor_input)
        probabilities = torch.softmax(output, dim=1)
        confidence, idx = torch.max(probabilities, 1)
        
        ai_pred = CLASS_NAMES[idx.item()]
        ai_conf = confidence.item()

    # ==========================================
    # TRỌNG TÀI DUNG HỢP (FUSION ENGINE) CHỐT HẠ KẾT QUẢ
    # ==========================================
    
    # LUẬT 1: THANH TRỪNG VPN / ẨN DANH HOÀN TOÀN
    # Nếu không có tên miền HOẶC AI đoán chắc nịch là VPN -> Khẳng định là luồng mã hóa -> VỨT!
    if not domain_lower or "VPN" in ai_pred:
        return "IGNORED"

    # LUẬT 2: Đồng thuận tuyệt đối
    if rule_pred == ai_pred:
        return rule_pred

    # LUẬT 3: Trọng tài phân xử lỗi Google Drive (Bác sĩ Rule chịu thua, nhường Bác sĩ AI)
    if rule_pred == 'google_ecosystem':
        if ai_pred in ['file_transfer', 'email']:
            return ai_pred # Tin tưởng AI 100%
        return 'file_transfer' # Mặc định CDN thường là tải file nặng

    # LUẬT 4: Trọng tài phân xử lỗi "Zalo Chat" vs "Zalo Gọi thoại"
    # Rule nhìn thấy zalo.me bảo là Chat. Nhưng AI đo thấy băng thông lớn, tốc độ nhả gói tin đều
    if rule_pred == 'chat' and ai_pred == 'VoIP' and ai_conf > 0.60:
        return 'VoIP' # AI chính xác hơn trong trường hợp này!

    # LUẬT 5: Rule-based bị mù (Gặp trang web mới tinh hoặc lướt web như Dân Trí)
    if rule_pred == 'UNKNOWN':
        # Nếu AI tự tin > 70% nó là 1 trong 5 nhãn Non-VPN thì nghe AI
        if ai_conf > 0.70 and ai_pred in ['Streaming', 'VoIP', 'chat', 'email', 'file_transfer']:
            return ai_pred
        # Trả về Unknown để hiển thị lên bảng Dashboard kèm tên miền
        return "Unknown" 

    # LUẬT 6: Trọng tài tôn trọng định danh cứng
    # VD: Rule bảo là Youtube, nhưng mạng lag làm AI tưởng lầm là Email. 
    # Do Youtube là tên miền tĩnh, Trọng tài bảo vệ kết quả của Rule.
    if rule_pred != 'UNKNOWN':
        return rule_pred

    # Mặc định an toàn
    return "Unknown"