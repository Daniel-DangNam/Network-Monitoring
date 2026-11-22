import { useState } from 'react';
import { UploadCloud, CheckCircle, AlertTriangle, Cpu, Globe } from 'lucide-react';
import { API_URL } from '../services/api';
import { getBadgeStyle, formatPredictionLabel } from '../utils/predictionColors';

export default function PcapAnalysis() {
    const [file, setFile] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
            setResult(null);
            setError(null);
        }
    };

    const handleUpload = async () => {
        if (!file) return;
        setIsLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await fetch(`${API_URL}/pcap/upload`, {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            if (res.ok) {
                setResult(data);
            } else {
                setError(data.detail || 'Lỗi khi phân tích tệp PCAP');
            }
        } catch (err) {
            setError('Không thể kết nối đến máy chủ: ' + err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div style={{ color: '#f8fafc' }}>
            <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '8px' }}>
                Phân Tích Tệp PCAP / PCAPNG
            </h2>
            <p style={{ color: '#94a3b8', fontSize: '14px', marginBottom: '24px' }}>
                Tải lên tệp ghi lưu lượng mạng để bóc tách luồng (Flows) và phân loại bằng AI thời gian thực (ĐATN).
            </p>

            {/* Khung tải lên tệp */}
            <div style={{
                background: '#0a0f1c',
                border: '2px dashed #334155',
                borderRadius: '12px',
                padding: '40px 20px',
                textAlign: 'center',
                marginBottom: '24px'
            }}>
                <UploadCloud size={48} color="#0ea5e9" style={{ margin: '0 auto 16px auto' }} />
                <h4 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '8px' }}>
                    Chọn hoặc Kéo thả tệp PCAP vào đây
                </h4>
                <p style={{ color: '#64748b', fontSize: '13px', marginBottom: '20px' }}>
                    Hỗ trợ các định dạng: .pcap, .pcapng, .cap (tối đa 100MB)
                </p>

                <input 
                    type="file" 
                    accept=".pcap,.pcapng,.cap" 
                    onChange={handleFileChange}
                    style={{ display: 'none' }}
                    id="pcap-upload-input"
                />
                <label 
                    htmlFor="pcap-upload-input"
                    style={{
                        background: '#1e293b',
                        color: '#f8fafc',
                        border: '1px solid #334155',
                        padding: '10px 20px',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontWeight: 'bold',
                        fontSize: '13px',
                        display: 'inline-block',
                        marginRight: '12px'
                    }}
                >
                    {file ? file.name : 'Duyệt tệp tin'}
                </label>

                {file && (
                    <button
                        onClick={handleUpload}
                        disabled={isLoading}
                        style={{
                            background: '#0ea5e9',
                            color: '#fff',
                            border: 'none',
                            padding: '10px 24px',
                            borderRadius: '6px',
                            cursor: isLoading ? 'not-allowed' : 'pointer',
                            fontWeight: 'bold',
                            fontSize: '13px'
                        }}
                    >
                        {isLoading ? 'Đang phân tích...' : 'Bắt đầu phân tích'}
                    </button>
                )}
            </div>

            {/* Thông báo lỗi */}
            {error && (
                <div style={{
                    background: 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid #ef4444',
                    borderRadius: '8px',
                    padding: '16px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    color: '#ef4444',
                    marginBottom: '24px'
                }}>
                    <AlertTriangle size={20} />
                    <span>{error}</span>
                </div>
            )}

            {/* Kết quả phân tích */}
            {result && (
                <div style={{
                    background: '#0a0f1c',
                    border: '1px solid #1e293b',
                    borderRadius: '12px',
                    padding: '24px'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
                        <CheckCircle size={22} color="#22c55e" />
                        <h3 style={{ fontSize: '18px', fontWeight: 'bold', margin: 0 }}>
                            Kết Quả Bóc Tách Tệp: {result.filename}
                        </h3>
                    </div>

                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                        gap: '16px',
                        marginBottom: '20px'
                    }}>
                        <div style={{ background: '#0f172a', padding: '16px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                            <span style={{ fontSize: '12px', color: '#64748b' }}>Kích thước tệp</span>
                            <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#0ea5e9', marginTop: '4px' }}>
                                {(result.file_size_bytes / 1024).toFixed(1)} KB
                            </div>
                        </div>

                        <div style={{ background: '#0f172a', padding: '16px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                            <span style={{ fontSize: '12px', color: '#64748b' }}>Tổng số Gói tin (Packets)</span>
                            <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#22c55e', marginTop: '4px' }}>
                                {result.total_packets.toLocaleString()}
                            </div>
                        </div>

                        <div style={{ background: '#0f172a', padding: '16px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                            <span style={{ fontSize: '12px', color: '#64748b' }}>Tổng số Luồng (5-Tuple Flows)</span>
                            <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#a855f7', marginTop: '4px' }}>
                                {result.total_flows.toLocaleString()}
                            </div>
                        </div>

                        <div style={{ background: '#0f172a', padding: '16px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                            <span style={{ fontSize: '12px', color: '#64748b' }}>Giao thức chính</span>
                            <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#eab308', marginTop: '4px' }}>
                                {result.protocol}
                            </div>
                        </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
                        <div style={{ background: '#0f172a', padding: '16px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                            <h4 style={{ fontSize: '13px', fontWeight: 'bold', marginBottom: '10px', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                <Cpu size={15} color="#38bdf8" /> Kết quả phân loại AI-Fusion:
                            </h4>
                            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
                                {(result.predicted_labels && result.predicted_labels.length > 0) ? (
                                    result.predicted_labels.map((lbl, idx) => (
                                        <span key={idx} style={getBadgeStyle(lbl)}>{formatPredictionLabel(lbl)}</span>
                                    ))
                                ) : (
                                    <span style={getBadgeStyle(result.summary_label)}>{formatPredictionLabel(result.summary_label)}</span>
                                )}
                            </div>
                        </div>

                        <div style={{ background: '#0f172a', padding: '16px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                            <h4 style={{ fontSize: '13px', fontWeight: 'bold', marginBottom: '10px', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                <Globe size={15} color="#22c55e" /> Tên miền & Thiết bị phát hiện:
                            </h4>
                            <p style={{ margin: '4px 0', fontSize: '13px', color: '#cbd5e1' }}>
                                <strong>Website/SNI:</strong> {(result.websites && result.websites.length > 0) ? result.websites.join(', ') : 'Không phát hiện tên miền'}
                            </p>
                            <p style={{ margin: '4px 0', fontSize: '13px', color: '#cbd5e1' }}>
                                <strong>Luồng tiêu biểu:</strong> {result.src_ip} &rarr; {result.dst_ip}
                            </p>
                            {result.client_ips && result.client_ips.length > 0 && (
                                <p style={{ margin: '4px 0', fontSize: '12px', color: '#38bdf8', fontFamily: 'monospace' }}>
                                    Client IP: {result.client_ips.join(', ')}
                                </p>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

