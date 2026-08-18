import { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import ControlPanel from '../components/ControlPanel';
import { Activity, Target, FileText } from 'lucide-react';

// Bảng màu cho các nhãn AI Prediction
const PREDICTION_COLORS = {
    'Normal': '#22c55e',      // Xanh lá
    'Streaming': '#3b82f6',   // Xanh dương
    'VoIP': '#eab308',        // Vàng cam
    'Malicious': '#ef4444',   // Đỏ
    'Anomaly': '#ef4444',     // Đỏ
    'Default': '#8b5cf6'      // Tím (Các nhãn khác)
};

export default function Dashboard() {
    const [logs, setLogs] = useState([]);
    const [isConnected, setIsConnected] = useState(false);

    useEffect(() => {
        const fetchInitialData = async () => {
            try {
                const token = localStorage.getItem('token');
                const res = await fetch('http://localhost:8000/api/v1/history', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const responseData = await res.json();
                
                if (responseData.data) {
                    const formattedLogs = responseData.data.slice(0, 50).map(item => ({
                        ...item,
                        timestamp: item.timestamp || item.log_timestamp 
                    }));
                    setLogs(formattedLogs);
                }
            } catch (error) {
                console.error("Lỗi lấy dữ liệu:", error);
            }
        };
        fetchInitialData();

        let ws = null;
        let reconnectTimeout = null;

        const connectWebSocket = () => {
            ws = new WebSocket('ws://localhost:8000/ws/realtime');
            ws.onopen = () => setIsConnected(true);
            ws.onmessage = (event) => {
                const newData = JSON.parse(event.data);
                setLogs(prevLogs => [newData, ...prevLogs].slice(0, 50));
            };
            ws.onclose = () => {
                setIsConnected(false);
                reconnectTimeout = setTimeout(connectWebSocket, 3000);
            };
            ws.onerror = () => ws.close();
        };

        connectWebSocket();

        return () => {
            if (ws) {
                ws.onclose = null;
                ws.close();
            }
            if (reconnectTimeout) clearTimeout(reconnectTimeout);
        };
    }, []);

    // Xử lý dữ liệu biểu đồ Area[cite: 16]
    const areaData = [...logs].slice(0, 20).reverse().map(log => {
        const timeObj = new Date(log.timestamp);
        return {
            time: isNaN(timeObj) ? log.timestamp.split(" ")[1] : timeObj.toLocaleTimeString('vi-VN', { hour12: false }),
            packets: log.packet_count
        };
    });

    // Xử lý dữ liệu biểu đồ Donut[cite: 16]
    const pieDataRaw = logs.reduce((acc, log) => {
        acc[log.ai_prediction] = (acc[log.ai_prediction] || 0) + 1;
        return acc;
    }, {});
    
    const pieData = Object.keys(pieDataRaw).map(key => ({
        name: key,
        value: pieDataRaw[key],
        color: PREDICTION_COLORS[key] || PREDICTION_COLORS['Default']
    }));

    const totalLogs = logs.length;

    // Hàm lấy màu cho Badge dựa trên tên nhãn
    const getBadgeStyle = (label) => {
        const color = PREDICTION_COLORS[label] || PREDICTION_COLORS['Default'];
        return {
            color: color,
            border: `1px solid ${color}`,
            background: `${color}15`, // Thêm độ trong suốt cho background
            padding: '4px 10px',
            borderRadius: '4px',
            fontSize: '12px',
            fontWeight: 'bold',
            display: 'inline-block'
        };
    };

    return (
        <div style={{ padding: '24px', background: '#050b14', minHeight: '100vh', color: '#e2e8f0' }}>
            
            <ControlPanel isConnected={isConnected} />

            {/* Khu vực Biểu đồ */}
            <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '20px', marginBottom: '20px' }}>
                
                {/* Area Chart */}
                <div style={{ background: '#0a0f1c', padding: '20px', borderRadius: '12px', border: '1px solid #1e293b' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
                        <Activity size={18} color="#94a3b8" />
                        <h3 style={{ margin: 0, fontSize: '14px', color: '#f8fafc' }}>Real-time Network Traffic (Packet Flow)</h3>
                    </div>
                    <div style={{ height: '220px', width: '100%' }}>
                        <ResponsiveContainer>
                            <AreaChart data={areaData}>
                                <defs>
                                    <linearGradient id="colorPackets" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.4}/>
                                        <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                                <XAxis dataKey="time" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                                <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                                <RechartsTooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', color: '#fff' }} />
                                <Area type="monotone" dataKey="packets" stroke="#0ea5e9" strokeWidth={2} fillOpacity={1} fill="url(#colorPackets)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Donut Chart */}
                <div style={{ background: '#0a0f1c', padding: '20px', borderRadius: '12px', border: '1px solid #1e293b', position: 'relative' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
                        <Target size={18} color="#94a3b8" />
                        <h3 style={{ margin: 0, fontSize: '14px', color: '#f8fafc' }}>AI Prediction Distribution</h3>
                    </div>
                    
                    <div style={{ display: 'flex', height: '220px' }}>
                        <div style={{ width: '60%', position: 'relative' }}>
                            <ResponsiveContainer>
                                <PieChart>
                                    <Pie data={pieData} cx="50%" cy="50%" innerRadius={55} outerRadius={80} paddingAngle={4} dataKey="value" stroke="none">
                                        {pieData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <RechartsTooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }} />
                                </PieChart>
                            </ResponsiveContainer>
                            {/* Text nằm giữa Donut Chart */}
                            <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center' }}>
                                <div style={{ fontSize: '12px', color: '#94a3b8' }}>Total</div>
                                <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#f8fafc' }}>{totalLogs}</div>
                            </div>
                        </div>
                        
                        {/* Legend tùy chỉnh bên phải */}
                        <div style={{ width: '40%', display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: '12px' }}>
                            {pieData.map((entry, index) => (
                                <div key={index} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '12px' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: entry.color }}></div>
                                        <span style={{ color: '#cbd5e1' }}>{entry.name}</span>
                                    </div>
                                    <span style={{ color: '#f8fafc', fontWeight: 'bold' }}>{entry.value}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* Bảng Log Real-time */}
            <div style={{ background: '#0a0f1c', borderRadius: '12px', border: '1px solid #1e293b', overflow: 'hidden' }}>
                <div style={{ padding: '16px 20px', borderBottom: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <FileText size={18} color="#94a3b8" />
                        <h3 style={{ margin: 0, fontSize: '14px', color: '#f8fafc' }}>LIVE PACKET LOG STREAM (WebSockets Real-time)</h3>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#22c55e' }}>
                        <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#22c55e', boxShadow: '0 0 6px #22c55e' }}></div>
                        Receiving Live Data
                    </div>
                </div>
                
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
                    <thead>
                        <tr style={{ background: 'rgba(15, 23, 42, 0.6)', color: '#94a3b8' }}>
                            <th style={{ padding: '12px 20px', fontWeight: 'normal' }}>Timestamp</th>
                            <th style={{ padding: '12px 20px', fontWeight: 'normal' }}>Packet Count</th>
                            <th style={{ padding: '12px 20px', fontWeight: 'normal' }}>AI Prediction Label</th>
                            <th style={{ padding: '12px 20px', fontWeight: 'normal' }}>Destination / Websites</th>
                        </tr>
                    </thead>
                    <tbody>
                        {logs.length === 0 ? (
                            <tr><td colSpan="4" style={{ textAlign: 'center', padding: '30px', color: '#64748b' }}>Đang chờ luồng dữ liệu...</td></tr>
                        ) : (
                            logs.slice(0, 10).map((log, index) => (
                                <tr key={index} style={{ borderBottom: '1px solid #1e293b', background: index % 2 === 0 ? 'transparent' : 'rgba(15, 23, 42, 0.3)' }}>
                                    <td style={{ padding: '14px 20px', color: '#cbd5e1' }}>
                                        {new Date(log.timestamp).toLocaleTimeString() !== "Invalid Date" ? log.timestamp.substring(0, 23) : log.timestamp}
                                    </td>
                                    <td style={{ padding: '14px 20px', color: '#f8fafc' }}>{log.packet_count}</td>
                                    <td style={{ padding: '14px 20px' }}>
                                        <span style={getBadgeStyle(log.ai_prediction)}>
                                            {log.ai_prediction}
                                        </span>
                                    </td>
                                    <td style={{ padding: '14px 20px', color: '#94a3b8' }}>
                                        {Array.isArray(log.websites) ? log.websites.join(", ") : log.websites}
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}