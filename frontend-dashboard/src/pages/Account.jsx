import { useState, useMemo } from 'react';
import { Users, ShieldCheck, UserPlus, CheckCircle, AlertCircle } from 'lucide-react';
import { registerUser } from '../services/api';

function parseJwtUsername(token) {
    if (!token) return 'admin';
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.sub || 'admin';
    } catch {
        return 'admin';
    }
}

export default function Account() {
    const token = localStorage.getItem('token');
    const currentUsername = useMemo(() => parseJwtUsername(token), [token]);

    const [newUsername, setNewUsername] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [statusMsg, setStatusMsg] = useState(null);
    const [isError, setIsError] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleCreateUser = async (e) => {
        e.preventDefault();
        if (!newUsername.trim() || newPassword.length < 4) {
            setIsError(true);
            setStatusMsg('Tên đăng nhập không được trống và mật khẩu tối thiểu 4 ký tự.');
            return;
        }
        setIsSubmitting(true);
        setStatusMsg(null);
        try {
            const res = await registerUser(newUsername.trim(), newPassword);
            setIsError(false);
            setStatusMsg(res.message || `Đã tạo tài khoản ${newUsername} thành công!`);
            setNewUsername('');
            setNewPassword('');
        } catch (err) {
            setIsError(true);
            setStatusMsg(err.message);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div style={{ padding: '24px', background: '#050b14', minHeight: '100vh', color: '#e2e8f0' }}>
            <div style={{ marginBottom: '24px' }}>
                <h2 style={{ margin: '0 0 6px 0', fontSize: '22px', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Users size={24} color="#0ea5e9" />
                    USER & ACCESS MANAGEMENT
                </h2>
                <p style={{ margin: 0, color: '#94a3b8', fontSize: '14px' }}>
                    Thông tin phiên đăng nhập quản trị và cấp tài khoản vận hành hệ thống
                </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
                {/* Thông tin phiên hiện tại */}
                <div style={{ background: '#0a0f1c', padding: '24px', borderRadius: '12px', border: '1px solid #1e293b' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                        <ShieldCheck size={22} color="#22c55e" />
                        <h3 style={{ margin: 0, fontSize: '16px', color: '#f8fafc' }}>Phiên Quản Trị Hiện Tại</h3>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '14px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px', background: '#0f172a', borderRadius: '8px', border: '1px solid #1e293b' }}>
                            <span style={{ color: '#94a3b8' }}>Tài khoản:</span>
                            <span style={{ color: '#38bdf8', fontWeight: 'bold' }}>{currentUsername}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px', background: '#0f172a', borderRadius: '8px', border: '1px solid #1e293b' }}>
                            <span style={{ color: '#94a3b8' }}>Vai trò:</span>
                            <span style={{ color: '#22c55e', fontWeight: 'bold' }}>Administrator</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px', background: '#0f172a', borderRadius: '8px', border: '1px solid #1e293b' }}>
                            <span style={{ color: '#94a3b8' }}>Cơ chế xác thực:</span>
                            <span style={{ color: '#cbd5e1' }}>JWT Bearer Token (HS256)</span>
                        </div>
                    </div>
                </div>

                {/* Tạo tài khoản mới */}
                <div style={{ background: '#0a0f1c', padding: '24px', borderRadius: '12px', border: '1px solid #1e293b' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                        <UserPlus size={22} color="#0ea5e9" />
                        <h3 style={{ margin: 0, fontSize: '16px', color: '#f8fafc' }}>Thêm Tài Khoản Giám Sát</h3>
                    </div>

                    <form onSubmit={handleCreateUser} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                        <div>
                            <label style={{ display: 'block', fontSize: '13px', color: '#94a3b8', marginBottom: '6px' }}>Tên đăng nhập mới</label>
                            <input
                                type="text"
                                value={newUsername}
                                onChange={(e) => setNewUsername(e.target.value)}
                                placeholder="Ví dụ: operator1"
                                style={{ width: '100%', padding: '10px 12px', background: '#0f172a', border: '1px solid #334155', borderRadius: '6px', color: '#f8fafc', fontSize: '14px', outline: 'none', boxSizing: 'border-box' }}
                            />
                        </div>
                        <div>
                            <label style={{ display: 'block', fontSize: '13px', color: '#94a3b8', marginBottom: '6px' }}>Mật khẩu</label>
                            <input
                                type="password"
                                value={newPassword}
                                onChange={(e) => setNewPassword(e.target.value)}
                                placeholder="Tối thiểu 4 ký tự"
                                style={{ width: '100%', padding: '10px 12px', background: '#0f172a', border: '1px solid #334155', borderRadius: '6px', color: '#f8fafc', fontSize: '14px', outline: 'none', boxSizing: 'border-box' }}
                            />
                        </div>

                        {statusMsg && (
                            <div style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                                padding: '10px 12px',
                                borderRadius: '6px',
                                fontSize: '13px',
                                background: isError ? 'rgba(239,68,68,0.1)' : 'rgba(34,197,94,0.1)',
                                border: `1px solid ${isError ? '#ef4444' : '#22c55e'}`,
                                color: isError ? '#ef4444' : '#22c55e'
                            }}>
                                {isError ? <AlertCircle size={16} /> : <CheckCircle size={16} />}
                                <span>{statusMsg}</span>
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={isSubmitting}
                            style={{
                                background: '#0ea5e9',
                                color: '#fff',
                                border: 'none',
                                padding: '10px 16px',
                                borderRadius: '6px',
                                fontWeight: 'bold',
                                cursor: isSubmitting ? 'not-allowed' : 'pointer',
                                fontSize: '14px'
                            }}
                        >
                            {isSubmitting ? 'Đang tạo...' : 'Tạo Tài Khoản'}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}
