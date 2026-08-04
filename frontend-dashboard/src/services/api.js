const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

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

export const getHistoryLogs = async (token) => {
    const response = await fetch(`${API_URL}/history`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });

    if (!response.ok) throw new Error('Không thể lấy lịch sử');
    return await response.json(); 
};