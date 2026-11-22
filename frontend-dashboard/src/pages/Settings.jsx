import { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Server, Cpu, Wifi, RefreshCw } from 'lucide-react';
import { API_BASE_URL, API_URL } from '../services/api';

export default function Settings() {
    const [health, setHealth] = useState(null);
    const [agentStatus, setAgentStatus] = useState(null);
    const [interfaces, setInterfaces] = useState([]);
    const [loading, setLoading] = useState(true);

    const loadDiagnostics = async (showSpinner = true) => {
        if (showSpinner) setLoading(true);
        try {
            const [hRes, aRes, iRes] = await Promise.all([
                fetch(`${API_BASE_URL}/health`).then(r => r.ok ? r.json() : null).catch(() => null),
                fetch(`${API_URL}/agent-status`).then(r => r.ok ? r.json() : null).catch(() => null),
                fetch(`${API_URL}/network-interfaces`).then(r => r.ok ? r.json() : null).catch(() => null),
            ]);
            setHealth(hRes);
            setAgentStatus(aRes);
            setInterfaces(iRes?.interfaces || []);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const timer = setTimeout(() => {
            loadDiagnostics(false);
        }, 0);
        return () => clearTimeout(timer);
    }, []);

    return (
        <div style={{ padding: '24px', background: '#050b14', minHeight: '100vh', color: '#e2e8f0' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <div>
                    <h2 style={{ margin: '0 0 6px 0', fontSize: '22px', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <SettingsIcon size={24} color="#0ea5e9" />
                        SYSTEM CONFIGURATION & DIAGNOSTICS
                    </h2>
                    <p style={{ margin: 0, color: '#94a3b8', fontSize: '14px' }}>
                        Thông số vận hành Backend API, mô hình AI và các card mạng đang kết nối
                    </p>
                </div>
                <button
                    onClick={loadDiagnostics}
                    style={{ background: '#1e293b', color: '#38bdf8', border: '1px solid #334155', padding: '8px 16px', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '13px', fontWeight: 'bold' }}
                >
                    <RefreshCw size={14} /> Làm mới trạng thái
                </button>
            </div>

            {loading ? (
                <div style={{ padding: '40px', textAlign: 'center', color: '#0ea5e9' }}>Đang kiểm tra trạng thái hệ thống...</div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
                    {/* Backend & API */}
                    <div style={{ background: '#0a0f1c', padding: '20px', borderRadius: '12px', border: '1px solid #1e293b' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                            <Server size={20} color="#22c55e" />
                            <h3 style={{ margin: 0, fontSize: '15px', color: '#f8fafc' }}>Máy Chủ Backend API</h3>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '13px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', background: '#0f172a', borderRadius: '6px' }}>
                                <span style={{ color: '#94a3b8' }}>Trạng thái:</span>
                                <span style={{ color: health ? '#22c55e' : '#ef4444', fontWeight: 'bold' }}>{health ? 'Healthy (Online)' : 'Offline'}</span>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', background: '#0f172a', borderRadius: '6px' }}>
                                <span style={{ color: '#94a3b8' }}>Phiên bản:</span>
                                <span style={{ color: '#f8fafc' }}>{health?.version || 'N/A'}</span>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', background: '#0f172a', borderRadius: '6px' }}>
                                <span style={{ color: '#94a3b8' }}>Endpoint API:</span>
                                <span style={{ color: '#38bdf8', fontFamily: 'monospace' }}>{API_BASE_URL}</span>
                            </div>
                        </div>
                    </div>

                    {/* Lõi AI & Sniffer */}
                    <div style={{ background: '#0a0f1c', padding: '20px', borderRadius: '12px', border: '1px solid #1e293b' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                            <Cpu size={20} color="#3b82f6" />
                            <h3 style={{ margin: 0, fontSize: '15px', color: '#f8fafc' }}>Cấu Hình AI Engine</h3>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '13px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', background: '#0f172a', borderRadius: '6px' }}>
                                <span style={{ color: '#94a3b8' }}>Kiến trúc:</span>
                                <span style={{ color: '#f8fafc', fontWeight: 'bold' }}>ResNet-18 + Rule Fusion</span>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', background: '#0f172a', borderRadius: '6px' }}>
                                <span style={{ color: '#94a3b8' }}>Bộ trích xuất:</span>
                                <span style={{ color: '#f8fafc' }}>CICFlowMeter (81 đặc trưng)</span>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', background: '#0f172a', borderRadius: '6px' }}>
                                <span style={{ color: '#94a3b8' }}>Trạng thái Agent:</span>
                                <span style={{ color: agentStatus?.is_running ? '#22c55e' : '#94a3b8', fontWeight: 'bold' }}>
                                    {agentStatus?.is_running ? `Đang chạy (PID ${agentStatus.pid || 'bg'})` : 'Đang chờ (Standby)'}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Card mạng phát hiện */}
                    <div style={{ background: '#0a0f1c', padding: '20px', borderRadius: '12px', border: '1px solid #1e293b' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                            <Wifi size={20} color="#eab308" />
                            <h3 style={{ margin: 0, fontSize: '15px', color: '#f8fafc' }}>Card Mạng Phát Hiện ({interfaces.length})</h3>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '13px' }}>
                            {interfaces.map((iface) => (
                                <div key={iface.name} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', background: '#0f172a', borderRadius: '6px' }}>
                                    <span style={{ color: '#38bdf8', fontFamily: 'monospace', fontWeight: 'bold' }}>{iface.name}</span>
                                    <span style={{ color: '#cbd5e1' }}>{iface.label}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
