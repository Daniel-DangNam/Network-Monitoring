import torch
import torch.nn as nn
import torchvision.models as models
import numpy as np

def main():
    print("1. Đang khởi tạo khuôn mạng ResNet-18 tùy chỉnh...")
    
    # Khởi tạo khung mạng ResNet-18 cơ bản
    model = models.resnet18(weights=None)
    
    # BẢN VÁ 1: Sửa kernel_size của conv1 từ 7x7 (mặc định) xuống 3x3 để khớp với file .pth
    model.conv1 = nn.Conv2d(
        in_channels=3, 
        out_channels=64, 
        kernel_size=3, 
        stride=1, 
        padding=1, 
        bias=False
    )
    
    # BẢN VÁ 2: Sửa lớp phân loại cuối cùng (fc) thành 11 classes thay vì 5
    num_ftrs = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(num_ftrs, 11) # Đổi thành 11 khớp với trọng số
    )
    
    # 2. Load trọng số từ file Checkpoint .pth
    try:
        checkpoint = torch.load('model_final_Application_Label.pth', map_location=torch.device('cpu'))
        
        if 'model_state_dict' in checkpoint:
            state_dict = checkpoint['model_state_dict']
        else:
            state_dict = checkpoint 
            
        model.load_state_dict(state_dict)
        model.eval()
        print("-> TẢI MÔ HÌNH THÀNH CÔNG 100%!")
    except Exception as e:
        print("\nLỗi tải file .pth. Chi tiết:", e)
        return

    # 3. Tạo dữ liệu giả lập (Ảnh 3 kênh màu RGB)
    print("\n2. Đang tạo dữ liệu giả lập để chạy thử...")
    # Vì dùng kernel 3x3, có khả năng kích thước ảnh gốc lúc train cũng khá nhỏ (VD: 9x9 hoặc 32x32)
    dummy_pixels = np.random.rand(1, 3, 32, 32) 
    tensor_input = torch.tensor(dummy_pixels, dtype=torch.float32)

    # 4. Đưa vào mô hình dự đoán
    print("3. Bắt đầu dự đoán...")
    with torch.no_grad():
        output = model(tensor_input)
        predicted_class = torch.argmax(output, dim=1).item()
    
    print(f"-> Kết quả test: Mô hình dự đoán thành công! Luồng dữ liệu thuộc Nhãn số {predicted_class} (trong tổng số từ 0 đến 10)")

if __name__ == "__main__":
    main()