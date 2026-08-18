import React from 'react';

export default function ProtectedRoute({ children, onNavigate }) {
    const token = localStorage.getItem('token');

    if (!token) {
        // Nếu chưa đăng nhập, chuyển hướng sang trang Login
        onNavigate('login');
        return null;
    }

    return children;
}