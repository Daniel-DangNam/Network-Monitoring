import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Activity, FileText, Users, Settings, LogOut } from 'lucide-react';

export default function Sidebar() {
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    // Hàm xử lý style linh hoạt cho mục đang Active[cite: 14]
    const linkStyle = (path) => {
        const isActive = location.pathname === path;
        return {
            color: isActive ? '#0ea5e9' : '#94a3b8',
            textDecoration: 'none',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '14px 20px',
            borderLeft: isActive ? '4px solid #0ea5e9' : '4px solid transparent',
            background: isActive ? 'linear-gradient(90deg, rgba(14,165,233,0.1) 0%, transparent 100%)' : 'transparent',
            fontWeight: isActive ? 'bold' : 'normal',
            transition: 'all 0.2s',
            fontSize: '14px'
        };
    };

    return (
        <aside style={{ width: '260px', background: '#0a0f1c', borderRight: '1px solid #1e293b', display: 'flex', flexDirection: 'column', height: '100%' }}>
            
            {/* Các liên kết điều hướng[cite: 14] */}
            <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginTop: '20px' }}>
                <Link to="/dashboard" style={linkStyle('/dashboard')}>
                    <Activity size={20} /> Dashboard
                </Link>
                <Link to="/history" style={linkStyle('/history')}>
                    <FileText size={20} /> Traffic History
                </Link>
                <Link to="/account" style={linkStyle('/account')}>
                    <Users size={20} /> User Management
                </Link>
                <Link to="/settings" style={linkStyle('/settings')}>
                    <Settings size={20} /> System Settings
                </Link>
            </nav>

            {/* Nút Đăng xuất ở cuối trang[cite: 14] */}
            <div style={{ marginTop: 'auto', padding: '20px' }}>
                <button 
                    onClick={handleLogout} 
                    style={{ 
                        background: 'transparent', 
                        border: 'none', 
                        color: '#ef4444', 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: '12px', 
                        padding: '12px 20px', 
                        cursor: 'pointer',
                        fontSize: '14px',
                        fontWeight: 'bold',
                        width: '100%',
                        transition: 'opacity 0.2s',
                        outline: 'none'
                    }}
                    onMouseOver={(e) => e.target.style.opacity = '0.8'}
                    onMouseOut={(e) => e.target.style.opacity = '1'}
                >
                    <LogOut size={20} /> Logout
                </button>
            </div>
        </aside>
    );
}