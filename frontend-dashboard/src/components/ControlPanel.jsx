import { useState, useEffect, useCallback } from 'react';
import { Zap, Play, Square, Activity, Clock } from 'lucide-react';

export default function ControlPanel({ isConnected }) {
    // Khôi phục trạng thái từ localStorage để khi chuyển tab không bị reset giao diện
    const [isListening, setIsListening] = useState(() => {
        return localStorage.getItem('agent_is_listening') === 'true';
    });
    const [isLoading, setIsLoading] = useState(false);
    const [adapterName, setAdapterName] = useState('auto (eth0/ens33)');
    const [duration, setDuration] = useState(() => {
        const saved = localStorage.getItem('agent_capture_duration');
        return saved ? Number(saved) : 30;
    });

    // Đồng bộ trạng thái Agent với Backend API
    const syncAgentStatus = useCallback(async () => {
        try {
            const response = await fetch('http://localhost:8000/api/v1/agent-status');
            if (response.ok) {
                const data = await response.json();
                const running = Boolean(data.is_running);
                setIsListening(running);
                localStorage.setItem('agent_is_listening', running ? 'true' : 'false');
                if (data.interface) {
                    setAdapterName(data.interface);
                }
            }
        } catch {
            // Backend có thể đang tắt hoặc mất kết nối tạm thời
        }
    }, []);

    useEffect(() => {
        // Đồng bộ ngay khi mount (chuyển từ tab khác sang)
        syncAgentStatus();

        // Định kỳ kiểm tra trạng thái mỗi 3 giây
        const intervalId = setInterval(syncAgentStatus, 3000);
        return () => clearInterval(intervalId);
    }, [syncAgentStatus]);

    // Hàm gọi API kích hoạt Network Agent
    const handleStart = async () => {
        setIsLoading(true);
        try {
            const response = await fetch('http://localhost:8000/api/v1/start-agent', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ duration: duration })
            });
            const data = await response.json();
            
            if (response.ok && (data.status === 'success' || data.status === 'info')) {
                setIsListening(true);
                localStorage.setItem('agent_is_listening', 'true');
                console.log("Hệ thống báo:", data.message);
            } else {
                alert("Lỗi từ máy chủ: " + (data.detail || data.message));
            }
        } catch (error) {
            console.error("Lỗi kết nối:", error);
            alert("Không thể kết nối đến Backend để kích hoạt!");
        } finally {
            setIsLoading(false);
            syncAgentStatus();
        }
    };

    // Hàm gọi API dừng Network Agent
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
                localStorage.setItem('agent_is_listening', 'false');
                console.log("Hệ thống báo:", data.message);
            } else {
                alert("Lỗi từ máy chủ: " + (data.detail || data.message));
            }
        } catch (error) {
            console.error("Lỗi kết nối:", error);
            alert("Không thể kết nối đến Backend để dừng!");
        } finally {
            setIsLoading(false);
            syncAgentStatus();
        }
    };

    return (
        <div style={{ 
            background: '#0a0f1c', 
            padding: '24px', 
            borderRadius: '12px', 
            marginBottom: '20px', 
            border: '1px solid #1e293b', 
            borderTop: isListening ? '2px solid #22c55e' : '2px solid #0ea5e9',
            boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center' 
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                <Zap 
                    size={28} 
                    color={isListening ? "#22c55e" : "#0ea5e9"} 
                    fill={isListening ? "#22c55e" : "#0ea5e9"} 
                    style={{ filter: `drop-shadow(0 0 8px ${isListening ? 'rgba(34,197,94,0.6)' : 'rgba(14,165,233,0.6)'})` }} 
                />
                <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', margin: '0 0 8px 0' }}>
                        <h3 style={{ margin: 0, fontSize: '18px', color: '#f8fafc', fontWeight: 'bold', letterSpacing: '0.5px' }}>
                            NETWORK CAPTURE CONTROL CENTER
                        </h3>
                        <span style={{
                            fontSize: '11px',
                            fontWeight: 'bold',
                            padding: '2px 8px',
                            borderRadius: '12px',
                            background: isListening ? 'rgba(34, 197, 94, 0.15)' : 'rgba(100, 116, 139, 0.2)',
                            color: isListening ? '#22c55e' : '#94a3b8',
                            border: `1px solid ${isListening ? '#22c55e' : '#475569'}`,
                            display: 'flex',
                            alignItems: 'center',
                            gap: '5px'
                        }}>
                            <span style={{
                                width: '6px',
                                height: '6px',
                                borderRadius: '50%',
                                background: isListening ? '#22c55e' : '#94a3b8',
                                boxShadow: isListening ? '0 0 6px #22c55e' : 'none'
                            }}></span>
                            {isListening ? 'ACTIVE SNIFFING' : 'STANDBY'}
                        </span>
                    </div>
                    <p style={{ margin: 0, fontSize: '13px', color: '#94a3b8' }}>
                        Adapter: <span style={{ color: '#0ea5e9', fontWeight: 'bold' }}>{adapterName}</span> | 
                        Chu kỳ: <span style={{ color: '#38bdf8', fontWeight: 'bold' }}>{duration}s</span> | 
                        WebSocket: {isConnected ? <span style={{ color: '#22c55e', fontWeight: 'bold' }}>Connected</span> : <span style={{ color: '#ef4444', fontWeight: 'bold' }}>Disconnected</span>}
                    </p>
                </div>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '8px', 
                    background: '#0f172a', 
                    padding: '8px 12px', 
                    borderRadius: '8px', 
                    border: '1px solid #1e293b' 
                }}>
                    <Clock size={16} color="#38bdf8" />
                    <span style={{ fontSize: '13px', color: '#94a3b8', fontWeight: '500' }}>Chu kỳ:</span>
                    <select 
                        value={duration} 
                        onChange={(e) => {
                            const val = Number(e.target.value);
                            setDuration(val);
                            localStorage.setItem('agent_capture_duration', val.toString());
                        }}
                        disabled={isListening || isLoading}
                        style={{
                            background: '#1e293b',
                            color: '#38bdf8',
                            border: '1px solid #334155',
                            borderRadius: '4px',
                            padding: '3px 8px',
                            fontSize: '13px',
                            fontWeight: 'bold',
                            outline: 'none',
                            cursor: (isListening || isLoading) ? 'not-allowed' : 'pointer'
                        }}
                    >
                        <option value={10}>10 giây</option>
                        <option value={15}>15 giây</option>
                        <option value={30}>30 giây (Mặc định)</option>
                        <option value={60}>60 giây</option>
                    </select>
                </div>

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
                        boxShadow: (isListening || isLoading) ? 'none' : '0 0 10px rgba(34,197,94,0.3)',
                        transition: 'all 0.2s'
                    }}
                >
                    <Play size={16} fill="currentColor" />
                    {isLoading && !isListening ? "STARTING..." : (isListening ? "Sniffing Active" : "Start Sniffing")}
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
                        boxShadow: (!isListening || isLoading) ? 'none' : '0 0 10px rgba(239,68,68,0.3)',
                        transition: 'all 0.2s'
                    }}
                >
                    <Square size={16} fill="currentColor" />
                    {isLoading && isListening ? "STOPPING..." : "Stop Sniffing"}
                </button>
            </div>
        </div>
    );
}