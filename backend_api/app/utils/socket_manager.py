from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # Kho chứa danh sách tất cả các "đường ống" đang cắm vào hệ thống (từ React, Ubuntu...)
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        # Chấp nhận kết nối và đưa vào danh sách quản lý
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        # Rút ống nước ra khi ai đó tắt trình duyệt
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        # Phát thanh trực tiếp cục dữ liệu JSON tới TẤT CẢ các màn hình đang mở
        for connection in self.active_connections:
            await connection.send_json(message)

# Đúc ra một "Trạm trưởng" duy nhất để điều phối
manager = ConnectionManager()