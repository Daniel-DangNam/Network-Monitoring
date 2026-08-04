import torch
import torch.nn as nn
import torchvision.models as models
import numpy as np

# Danh sách 11 nhãn theo đúng thứ tự (0-10)
CLASS_NAMES = [
    'Streaming', 'VPN-VoIP', 'VPN-chat', 'VPN-email', 'VPN-file_transfer',
    'VPN-p2p', 'VPN-streaming', 'VoIP', 'chat', 'email', 'file_transfer'
]

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
    # CHỈNH SỬA Ở ĐÂY: Tự động đệm số 0 cho đủ 81 phần tử (9x9)
    features_81 = list(features_list)
    
    if len(features_81) < 81:
        # Nếu thiếu (ví dụ có 78), đệm thêm các số 0 vào cuối
        padding_needed = 81 - len(features_81)
        features_81.extend([0.0] * padding_needed)
    elif len(features_81) > 81:
        # Nếu thừa, chỉ lấy đúng 81 cái đầu tiên
        features_81 = features_81[:81]
    
    arr = np.array(features_81, dtype=np.float32)
    
    # Chuẩn hóa Min-Max
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