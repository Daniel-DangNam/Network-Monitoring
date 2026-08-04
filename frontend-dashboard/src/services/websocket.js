let socket = null;
const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws/realtime";

export const connectWebSocket = (onMessage, onStatusChange) => {
    socket = new WebSocket(WS_URL);

    socket.onopen = () => {
        console.log("🟢 Kết nối WebSocket thành công!");
        onStatusChange(true);
    };

    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            onMessage(data); // Trả payload { id, ai_prediction, packet_count, websites, timestamp } về UI[cite: 6]
        } catch (err) {
            console.error("Lỗi parse JSON:", err);
        }
    };

    socket.onclose = () => {
        console.log("🔴 Mất kết nối WebSocket. Đang thử lại...");
        onStatusChange(false);
        setTimeout(() => connectWebSocket(onMessage, onStatusChange), 3000);
    };

    socket.onerror = (err) => {
        console.error("WebSocket Error:", err);
    };
};

export const disconnectWebSocket = () => {
    if (socket) socket.close();
};