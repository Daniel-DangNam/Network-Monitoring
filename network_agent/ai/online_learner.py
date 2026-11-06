import numpy as np
from typing import Dict, Any, Optional

class OnlineTrafficClassifier:
    """
    Lớp xử lý Online Machine Learning (Học máy trực tuyến) cho ĐATN.
    Hỗ trợ học từng mẫu (sample-by-sample) hoặc mini-batch và thích ứng với Concept Drift.
    """
    def __init__(self, n_features: int = 81):
        self.n_features = n_features
        self.classes_ = [
            'Streaming', 'VPN-VoIP', 'VPN-chat', 'VPN-email', 'VPN-file_transfer',
            'VPN-p2p', 'VPN-streaming', 'VoIP', 'chat', 'email', 'file_transfer'
        ]
        self._model = None
        self._init_model()

    def _init_model(self):
        try:
            from sklearn.linear_model import SGDClassifier
            self._model = SGDClassifier(loss="log_loss", penalty="l2", alpha=1e-4, random_state=42)
            # Khởi tạo partial_fit với nhãn rỗng
            dummy_x = np.zeros((len(self.classes_), self.n_features))
            self._model.partial_fit(dummy_x, self.classes_, classes=self.classes_)
            print("[Online ML] Khởi tạo mô hình SGD Online Learning thành công.")
        except Exception as e:
            print(f"[Online ML] Cảnh báo khi khởi tạo SGD: {e}")

    def learn_one(self, x: np.ndarray, y: str):
        """Học tăng cường một mẫu dữ liệu luồng mạng mới (Incremental Fit)"""
        if self._model is None:
            return
        x_reshaped = np.array(x).reshape(1, -1)
        self._model.partial_fit(x_reshaped, [y])

    def predict_one(self, x: np.ndarray) -> tuple[str, float]:
        """Dự đoán nhãn và độ tự tin cho 1 vector đặc trưng"""
        if self._model is None:
            return ("Unknown", 0.0)
        x_reshaped = np.array(x).reshape(1, -1)
        try:
            probs = self._model.predict_proba(x_reshaped)[0]
            max_idx = np.argmax(probs)
            return (self.classes_[max_idx], float(probs[max_idx]))
        except Exception:
            pred = self._model.predict(x_reshaped)[0]
            return (pred, 0.5)

online_classifier = OnlineTrafficClassifier()

