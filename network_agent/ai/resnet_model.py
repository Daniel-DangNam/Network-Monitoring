import torch
import torch.nn as nn
import torchvision.models as models
import numpy as np

def load_ai_model(model_path):
    print(f"[AI] Đang nạp cấu trúc ResNet-18 từ {model_path}...")
    model = models.resnet18(weights=None)
    model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
    num_ftrs = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(num_ftrs, 11)
    )
    checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
    if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
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
    arr = np.nan_to_num(arr, nan=0.0, posinf=1.0, neginf=0.0)
    
    arr_min, arr_max = np.min(arr), np.max(arr)
    if arr_max - arr_min != 0:
        arr_normalized = (arr - arr_min) / (arr_max - arr_min)
    else:
        arr_normalized = arr - arr_min
        
    image_9x9 = arr_normalized.reshape(9, 9)
    image_rgb = np.stack([image_9x9, image_9x9, image_9x9], axis=0)
    return torch.tensor(np.expand_dims(image_rgb, axis=0), dtype=torch.float32)

