import pandas as pd
from ai_core import load_ai_model, features_to_tensor, predict

def main():
    print("--- BẮT ĐẦU CHƯƠNG TRÌNH PHÂN TÍCH ---")
    
    model_path = 'model_final_Application_Label.pth'
    model = load_ai_model(model_path)
    
    # Thêm chữ 'r' để biến thành Raw String, tránh lỗi \T
    csv_file = r'd:\Thực tập tốt nghiệp\dataset\CIC-IDS2017\CSV\MachineLearningCVE\Monday-WorkingHours.pcap_ISCX.csv'
    
    print(f"\n[Data] Đang đọc luồng dữ liệu từ: {csv_file}")
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy {csv_file}. Vui lòng kiểm tra lại thư mục.")
        return

    # Lọc bỏ các cột chứa chữ, chỉ giữ lại các cột chứa số
    df_numeric = df.select_dtypes(include=['number'])
    num_cols = df_numeric.shape[1]
    
    # Giảm mức kiểm tra xuống 70 để tương thích với CIC-IDS2017
    if num_cols < 70:
        print(f"Lỗi: File CSV quá ít đặc trưng ({num_cols} cột).")
        return
        
    # Trích xuất toàn bộ dữ liệu số của dòng đầu tiên
    row_data = df_numeric.iloc[0, :].tolist()
    print(f"[Data] Đã trích xuất thành công {num_cols} đặc trưng của luồng mạng!")
    
    print("\n[Process] Đang chuyển đổi dữ liệu thành ảnh Tensor và dự đoán...")
    tensor_data = features_to_tensor(row_data)
    result = predict(model, tensor_data)
    
    print(f"\n=========================================")
    print(f" KẾT QUẢ PHÂN TÍCH LUỒNG: {result}")
    print(f"=========================================\n")

if __name__ == "__main__":
    main()