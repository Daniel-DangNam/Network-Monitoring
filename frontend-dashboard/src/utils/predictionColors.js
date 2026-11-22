// Bảng màu phân biệt rõ 5 nhóm hành vi ứng dụng + các nhãn hệ thống
export const PREDICTION_COLORS = {
    'Streaming': '#3b82f6',       // Xanh dương
    'VoIP': '#eab308',            // Vàng cam
    'chat': '#22c55e',            // Xanh lá
    'Chat': '#22c55e',            // Xanh lá
    'email': '#a855f7',           // Tím
    'Email': '#a855f7',           // Tím
    'file_transfer': '#06b6d4',   // Xanh ngọc (Cyan)
    'File Transfer': '#06b6d4',   // Xanh ngọc
    'Normal': '#22c55e',
    'Malicious': '#ef4444',
    'Anomaly': '#ef4444',
    'Unknown': '#64748b',         // Xám
    'Default': '#8b5cf6'
};

export const PREDICTION_DISPLAY_NAMES = {
    'Streaming': 'Streaming',
    'VoIP': 'VoIP',
    'chat': 'Chat',
    'email': 'Email',
    'file_transfer': 'File Transfer',
    'Unknown': 'Unknown'
};

export function getPredictionColor(label) {
    return PREDICTION_COLORS[label] || PREDICTION_COLORS['Default'];
}

export function formatPredictionLabel(label) {
    return PREDICTION_DISPLAY_NAMES[label] || label || 'Unknown';
}

export function getBadgeStyle(label) {
    const color = getPredictionColor(label);
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
}
