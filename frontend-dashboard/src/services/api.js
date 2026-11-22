const currentHost = typeof window !== 'undefined' && window.location.hostname ? window.location.hostname : 'localhost';

export const API_BASE_URL = import.meta.env.VITE_API_ORIGIN || `http://${currentHost}:8000`;
export const API_URL = import.meta.env.VITE_API_URL || `${API_BASE_URL}/api/v1`;
export const WS_URL = import.meta.env.VITE_WS_URL || `${typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss' : 'ws'}://${currentHost}:8000/ws/realtime`;

export const loginUser = async (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
    });

    if (!response.ok) throw new Error('Đăng nhập thất bại');
    return await response.json();
};

export const registerUser = async (username, password) => {
    const response = await fetch(`${API_URL}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Tạo tài khoản thất bại');
    return data;
};

export const getHistoryLogs = async (token) => {
    const response = await fetch(`${API_URL}/history`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });

    if (!response.ok) throw new Error('Không thể lấy lịch sử');
    return await response.json();
};
