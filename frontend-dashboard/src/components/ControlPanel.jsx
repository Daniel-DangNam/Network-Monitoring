import { useState } from 'react';
import { Zap, Play, Square } from 'lucide-react';

export default function ControlPanel({ isConnected }) {
    const [isListening, setIsListening] = useState(false);
    const [isLoading, setIsLoading] = useState(false); // Trạng thái chờ API phản hồi[cite: 15]

    // Hàm gọi API kích hoạt Network Agent[cite: 15]
    const handleStart = async () => {
        setIsLoading(true);
        try {
            const response = await fetch('http://localhost:8000/api/v1/start-agent', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();
            
            if (response.ok && (data.status === 'success' || data.status === 'info')) {
                setIsListening(true);
                console.log("Hệ thống báo:", data.message);
            } else {
                alert("Lỗi từ máy chủ: " + data.detail);
            }
        } catch (error) {
            console.error("Lỗi kết nối:", error);
            alert("Không thể kết nối đến Backend để kích hoạt!");
        } finally {
            setIsLoading(false);
        }
    };

    // Hàm gọi API dừng Network Agent[cite: 15]
    const handleStop = async () => {
        setIsLoading(true);
        try {
            const response = await fetch('http://localhost:8000/api/v1/stop-agent', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();
            
            if (response.ok && (data.status === 'success' || data.status === 'info')) {
                setIsListening(false);
                console.log("Hệ thống báo:", data.message);
            } else {
                alert("Lỗi từ máy chủ: " + data.detail);
            }
        } catch (error) {
            console.error("Lỗi kết nối:", error);
            alert("Không thể kết nối đến Backend để dừng!");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div style={{ 
            background: '#0a0f1c', 
            padding: '24px', 
            borderRadius: '12px', 
            marginBottom: '20px', 
            border: '1px solid #1e293b', 
            borderTop: '2px solid #0ea5e9', // Viền xanh neon phía trên
            boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center' 
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                <Zap size={28} color="#0ea5e9" fill="#0ea5e9" style={{ filter: 'drop-shadow(0 0 8px rgba(14,165,233,0.6))' }} />
                <div>
                    <h3 style={{ margin: '0 0 8px 0', fontSize: '18px', color: '#f8fafc', fontWeight: 'bold', letterSpacing: '0.5px' }}>
                        NETWORK CAPTURE CONTROL CENTER
                    </h3>
                    <p style={{ margin: 0, fontSize: '13px', color: '#94a3b8' }}>
                        Adapter: <span style={{ color: '#0ea5e9', fontWeight: 'bold' }}>eth0</span> | 
                        Mode: <span style={{ color: '#0ea5e9', fontWeight: 'bold' }}>Reverse Connect</span> | 
                        WebSocket: {isConnected ? <span style={{ color: '#22c55e', fontWeight: 'bold' }}>Connected</span> : <span style={{ color: '#ef4444', fontWeight: 'bold' }}>Disconnected</span>}
                    </p>
                </div>
            </div>
            
            <div style={{ display: 'flex', gap: '15px' }}>
                <button 
                    onClick={handleStart} 
                    disabled={isListening || isLoading}
                    style={{ 
                        background: (isListening || isLoading) ? '#1e293b' : 'linear-gradient(180deg, rgba(21,128,61,0.2) 0%, rgba(21,128,61,0.8) 100%)', 
                        color: (isListening || isLoading) ? '#64748b' : '#fff', 
                        border: (isListening || isLoading) ? '1px solid #334155' : '1px solid #22c55e', 
                        padding: '10px 24px', 
                        borderRadius: '6px', 
                        cursor: (isListening || isLoading) ? 'not-allowed' : 'pointer', 
                        fontWeight: 'bold',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        boxShadow: (isListening || isLoading) ? 'none' : '0 0 10px rgba(34,197,94,0.3)'
                    }}
                >
                    <Play size={16} fill="currentColor" />
                    {isLoading && !isListening ? "STARTING..." : "Start Sniffing"}
                </button>
                <button 
                    onClick={handleStop} 
                    disabled={!isListening || isLoading}
                    style={{ 
                        background: (!isListening || isLoading) ? '#1e293b' : 'linear-gradient(180deg, rgba(185,28,28,0.2) 0%, rgba(185,28,28,0.8) 100%)', 
                        color: (!isListening || isLoading) ? '#64748b' : '#fff', 
                        border: (!isListening || isLoading) ? '1px solid #334155' : '1px solid #ef4444', 
                        padding: '10px 24px', 
                        borderRadius: '6px', 
                        cursor: (!isListening || isLoading) ? 'not-allowed' : 'pointer', 
                        fontWeight: 'bold',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        boxShadow: (!isListening || isLoading) ? 'none' : '0 0 10px rgba(239,68,68,0.3)'
                    }}
                >
                    <Square size={16} fill="currentColor" />
                    {isLoading && isListening ? "STOPPING..." : "Stop Sniffing"}
                </button>
            </div>
        </div>
    );
}