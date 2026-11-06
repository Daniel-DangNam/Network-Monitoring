import torch
from network_agent.ai.rules import CLASS_NAMES, SNI_RULES_ADVANCED

def parallel_fusion_predict(model, tensor_input, sni_domain, protocol, dst_port=0):
    """
    Hệ thống Dung hợp Quyết định (Decision-Level Fusion)
    Chạy song song Rule-Based và AI, sau đó Trọng tài phân xử.
    """
    domain_lower = str(sni_domain).lower().strip() if sni_domain else ""
    is_anonymous = domain_lower in ['', 'none', 'unknown', 'nan']
    
    # ==========================================
    # BÁC SĨ 1: RULE-BASED (Khám bằng Tên miền)
    # ==========================================
    rule_pred = "UNKNOWN"
    
    # ---> VÁ LỖI CỨU CÁNH CHO LUỒNG GOOGLE MEET/VOIP ẨN DANH <---
    if is_anonymous and protocol == 17 and (dst_port == 3478 or dst_port == 443 or dst_port >= 10000):
        rule_pred = 'VoIP'
        
    # NẾU CÓ TÊN MIỀN RÕ RÀNG
    elif not is_anonymous:
        # Xử lý Cú lừa hệ sinh thái Google 
        if 'googleusercontent.com' in domain_lower:
            subdomain = domain_lower.split('.googleusercontent.com')[0]
            if subdomain.startswith('ci') or 'mail' in subdomain or subdomain.startswith('lh'):
                rule_pred = 'email'
            else:
                rule_pred = 'google_ecosystem'
                
        # ---> VÁ LỖI GOOGLE MEET VÀ HỌP TRỰC TUYẾN KHI BẮT ĐƯỢC TÊN MIỀN <---
        elif any(app in domain_lower for app in ['meet.google', 'zoom', 'teams', 'webex']):
            rule_pred = 'VoIP'
            
        # Ưu tiên các app có thể vừa Chat vừa Gọi điện (Zalo, Tele, Messenger)
        elif any(app in domain_lower for app in ['zalo', 'zadn.vn', 'telegram', 'messenger', 'discord', 'skype']):
            rule_pred = 'chat'
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
        
    core_ai_pred = ai_pred.replace('VPN-', '')
    if core_ai_pred == 'streaming':
        core_ai_pred = 'Streaming'

    # ==========================================
    # TRỌNG TÀI DUNG HỢP (FUSION ENGINE) CHỐT HẠ KẾT QUẢ
    # ==========================================
    
    # LUẬT 1: THANH TRỪNG VPN / ẨN DANH HOÀN TOÀN
    if is_anonymous and rule_pred != 'VoIP' and "VPN" in ai_pred:
        return "IGNORED"

    # LUẬT 2: Đồng thuận tuyệt đối
    if rule_pred == ai_pred or rule_pred == core_ai_pred:
        return rule_pred

    # LUẬT 3: Trọng tài phân xử lỗi Google Drive
    if rule_pred == 'google_ecosystem':
        if core_ai_pred in ['file_transfer', 'email']:
            return core_ai_pred
        return 'file_transfer'

    # LUẬT 4: Trọng tài phân xử lỗi "Zalo Chat" vs "Zalo Gọi thoại"
    if rule_pred == 'chat' and core_ai_pred == 'VoIP' and ai_conf > 0.50:
        return 'VoIP'

    # LUẬT 5: Rule-based bị mù
    if rule_pred == 'UNKNOWN':
        if ai_conf > 0.50 and core_ai_pred in ['Streaming', 'VoIP', 'chat', 'email', 'file_transfer']:
            return core_ai_pred
        return "Unknown" 

    # LUẬT 6: Trọng tài tôn trọng định danh cứng
    if rule_pred != 'UNKNOWN':
        return rule_pred

    return "Unknown"

