import { useState, useEffect } from 'react';
import { getHistoryLogs } from '../services/api';
import { Database, Filter, Download, FileText } from 'lucide-react';
import jsPDF from 'jspdf';
import 'jspdf-autotable';

// Bảng màu chuẩn hóa cho các nhãn AI
const PREDICTION_COLORS = {
    'Normal': '#22c55e',      // Xanh lá
    'Streaming': '#3b82f6',   // Xanh dương
    'VoIP': '#eab308',        // Vàng cam
    'Malicious': '#ef4444',   // Đỏ
    'Anomaly': '#ef4444',     // Đỏ
    'Default': '#8b5cf6'      // Tím
};

export default function History() {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    
    // Các State phục vụ phân trang
    const [currentPage, setCurrentPage] = useState(1);
    const [itemsPerPage] = useState(15);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const token = localStorage.getItem('token');
                const res = await getHistoryLogs(token);
                setHistory(res.data || []);
            } catch (err) {
                console.error("Lỗi lấy lịch sử:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchHistory();
    }, []);

    // ----------------------------------------------------
    // HÀM XUẤT FILE CSV TRỰC TIẾP TỪ STATE FRONTEND
    // ----------------------------------------------------
    const exportToCSV = () => {
        if (history.length === 0) return alert("Không có dữ liệu để xuất!");
        
        const headers = ['ID', 'Timestamp', 'Packet Count', 'AI Prediction Label', 'Destination / Websites'];
        
        const csvRows = history.map(item => {
            const websites = Array.isArray(item.websites) ? item.websites.join('; ') : (item.websites || '');
            const time = new Date(item.log_timestamp).toLocaleString('vi-VN');
            // Bọc trong dấu ngoặc kép để tránh lỗi dấu phẩy trong chuỗi
            return `${item.id},"${time}","${item.packet_count}","${item.ai_prediction}","${websites}"`;
        });
        
        // Thêm BOM (\uFEFF) để Excel đọc tiếng Việt UTF-8 không bị lỗi font
        const csvContent = "\uFEFF" + [headers.join(','), ...csvRows].join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `Network_Log_${new Date().getTime()}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    // ----------------------------------------------------
    // HÀM XUẤT FILE PDF SỬ DỤNG jspdf VÀ jspdf-autotable
    // ----------------------------------------------------
    const exportToPDF = () => {
        if (history.length === 0) return alert("Không có dữ liệu để xuất!");
        
        const doc = new jsPDF();
        
        // Cài đặt tiêu đề
        doc.setFontSize(16);
        doc.text("Network Traffic Classification Report", 14, 15);
        doc.setFontSize(10);
        doc.text(`Generated at: ${new Date().toLocaleString('vi-VN')}`, 14, 22);
        
        const tableColumn = ["ID", "Time", "Packets", "AI Label", "Destination"];
        const tableRows = [];
        
        history.forEach(log => {
            const websites = Array.isArray(log.websites) ? log.websites.join(', ') : (log.websites || '');
            const logData = [
                log.id, 
                new Date(log.log_timestamp).toLocaleString('vi-VN'), 
                log.packet_count, 
                log.ai_prediction, 
                websites
            ];
            tableRows.push(logData);
        });
        
        doc.autoTable({
            head: [tableColumn],
            body: tableRows,
            startY: 28,
            theme: 'striped',
            headStyles: { fillColor: [14, 165, 233] },
            styles: { fontSize: 9 }
        });
        
        doc.save(`Network_Report_${new Date().getTime()}.pdf`);
    };

    // Hàm lấy màu cho Badge dựa trên tên nhãn
    const getBadgeStyle = (label) => {
        const color = PREDICTION_COLORS[label] || PREDICTION_COLORS['Default'];
        return {
            color: color,
            border: `1px solid ${color}`,
            background: `${color}15`,
            padding: '4px 10px',
            borderRadius: '4px',
            fontSize: '12px',
            fontWeight: 'bold',
            display: 'inline-block'
        };
    };

    // Xử lý logic phân trang
    const totalPages = Math.ceil(history.length / itemsPerPage);
    const indexOfLastItem = currentPage * itemsPerPage;
    const indexOfFirstItem = indexOfLastItem - itemsPerPage;
    const currentItems = history.slice(indexOfFirstItem, indexOfLastItem);

    return (
        <div style={{ padding: '24px', background: '#050b14', minHeight: '100vh', color: '#e2e8f0' }}>
            
            {/* Header Trang */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <div>
                    <h2 style={{ margin: '0 0 5px 0', fontSize: '22px', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <Database size={24} color="#0ea5e9" />
                        TRAFFIC HISTORY ARCHIVE
                    </h2>
                    <p style={{ margin: 0, color: '#94a3b8', fontSize: '14px' }}>Truy xuất và xem lại toàn bộ lịch sử phân tích từ PostgreSQL</p>
                </div>
                
                {/* NHÓM NÚT XUẤT BÁO CÁO */}
                <div style={{ display: 'flex', gap: '12px' }}>
                    <button 
                        onClick={exportToCSV}
                        style={{ 
                            background: 'rgba(14, 165, 233, 0.1)', color: '#0ea5e9', border: '1px solid rgba(14, 165, 233, 0.3)', 
                            padding: '8px 16px', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontWeight: 'bold'
                        }}>
                        <Download size={16} /> Xuất CSV
                    </button>
                    
                    <button 
                        onClick={exportToPDF}
                        style={{ 
                            background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', border: '1px solid rgba(239, 68, 68, 0.3)', 
                            padding: '8px 16px', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontWeight: 'bold'
                        }}>
                        <FileText size={16} /> Xuất PDF
                    </button>
                </div>
            </div>

            {/* Thanh công cụ (Bộ lọc) */}
            <div style={{ background: '#0a0f1c', padding: '16px 20px', borderRadius: '12px 12px 0 0', border: '1px solid #1e293b', borderBottom: 'none', display: 'flex', alignItems: 'center' }}>
                <button style={{ background: '#1e293b', color: '#cbd5e1', border: '1px solid #334155', padding: '8px 16px', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '13px' }}>
                    <Filter size={14} /> Lọc theo nhãn
                </button>
            </div>

            {/* Bảng dữ liệu */}
            <div style={{ background: '#0a0f1c', borderRadius: '0 0 12px 12px', border: '1px solid #1e293b', overflow: 'hidden' }}>
                {loading ? (
                    <div style={{ padding: '40px', textAlign: 'center', color: '#0ea5e9' }}>⏳ Đang tải dữ liệu từ trung tâm dữ liệu...</div>
                ) : (
                    <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
                        <thead>
                            <tr style={{ background: 'rgba(15, 23, 42, 0.6)', color: '#94a3b8' }}>
                                <th style={{ padding: '14px 20px', fontWeight: 'normal' }}>ID</th>
                                <th style={{ padding: '14px 20px', fontWeight: 'normal' }}>Timestamp</th>
                                <th style={{ padding: '14px 20px', fontWeight: 'normal' }}>Packet Count</th>
                                <th style={{ padding: '14px 20px', fontWeight: 'normal' }}>AI Prediction Label</th>
                                <th style={{ padding: '14px 20px', fontWeight: 'normal' }}>Destination / Websites</th>
                            </tr>
                        </thead>
                        <tbody>
                            {currentItems.length === 0 ? (
                                <tr>
                                    <td colSpan="5" style={{ padding: '30px', textAlign: 'center', color: '#64748b' }}>
                                        Không tìm thấy bản ghi nào.
                                    </td>
                                </tr>
                            ) : (
                                currentItems.map((item, index) => (
                                    <tr key={item.id} style={{ borderBottom: '1px solid #1e293b', background: index % 2 === 0 ? 'transparent' : 'rgba(15, 23, 42, 0.3)' }}>
                                        <td style={{ padding: '14px 20px', color: '#64748b' }}>#{item.id}</td>
                                        <td style={{ padding: '14px 20px', color: '#cbd5e1' }}>
                                            {new Date(item.log_timestamp).toLocaleString('vi-VN')}
                                        </td>
                                        <td style={{ padding: '14px 20px', color: '#f8fafc', fontWeight: 'bold' }}>{item.packet_count}</td>
                                        <td style={{ padding: '14px 20px' }}>
                                            <span style={getBadgeStyle(item.ai_prediction)}>
                                                {item.ai_prediction}
                                            </span>
                                        </td>
                                        <td style={{ padding: '14px 20px', color: '#94a3b8' }}>
                                            {Array.isArray(item.websites) ? item.websites.join(', ') : item.websites}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                )}

                {/* Footer Phân trang */}
                {!loading && history.length > 0 && (
                    <div style={{ padding: '16px 20px', borderTop: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '13px', color: '#94a3b8' }}>
                        <div>
                            Hiển thị {indexOfFirstItem + 1} - {Math.min(indexOfLastItem, history.length)} trong tổng số {history.length} bản ghi
                        </div>
                        <div style={{ display: 'flex', gap: '8px' }}>
                            <button 
                                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                                disabled={currentPage === 1}
                                style={{ background: '#1e293b', border: 'none', color: currentPage === 1 ? '#475569' : '#cbd5e1', padding: '6px 12px', borderRadius: '6px', cursor: currentPage === 1 ? 'not-allowed' : 'pointer' }}
                            >
                                Trước
                            </button>
                            <span style={{ padding: '6px 12px', background: 'rgba(14, 165, 233, 0.1)', color: '#0ea5e9', borderRadius: '6px', fontWeight: 'bold' }}>
                                Trang {currentPage} / {totalPages}
                            </span>
                            <button 
                                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                                disabled={currentPage === totalPages}
                                style={{ background: '#1e293b', border: 'none', color: currentPage === totalPages ? '#475569' : '#cbd5e1', padding: '6px 12px', borderRadius: '6px', cursor: currentPage === totalPages ? 'not-allowed' : 'pointer' }}
                            >
                                Sau
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}