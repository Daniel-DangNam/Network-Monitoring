import { Shield, Search, Settings, User } from 'lucide-react';

export default function Navbar() {
    return (
        <header style={{ 
            background: '#0a0f1c', 
            color: '#fff', 
            padding: '12px 24px', 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            borderBottom: '1px solid #1e293b',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
        }}>
            {/* Cụm Logo bên trái */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: '240px' }}>
                <div style={{ background: '#0ea5e9', padding: '6px', borderRadius: '8px', display: 'flex', boxShadow: '0 0 10px rgba(14, 165, 233, 0.3)' }}>
                    <Shield size={24} color="#fff" />
                </div>
                <strong style={{ fontSize: '17px', letterSpacing: '1px', fontWeight: '700' }}>
                    NETWORK AI MONITOR
                </strong>
            </div>

            {/* Ô tìm kiếm ở giữa */}
            <div style={{ flex: 1, display: 'flex', justifyContent: 'flex-start', paddingLeft: '40px' }}>
                <div style={{ display: 'flex', alignItems: 'center', background: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px', padding: '10px 16px', width: '450px', transition: 'border-color 0.3s' }}>
                    <Search size={18} color="#64748b" style={{ marginRight: '10px' }} />
                    <input 
                        type="text" 
                        placeholder="[ Search logs, IPs, Labels... ]" 
                        style={{ background: 'transparent', border: 'none', color: '#f8fafc', outline: 'none', width: '100%', fontSize: '13px' }} 
                    />
                </div>
            </div>

            {/* Cụm chức năng & Avatar bên phải */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
                
                {/* Trạng thái Agent */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', border: '1px solid rgba(34, 197, 94, 0.3)', padding: '6px 16px', borderRadius: '20px', background: 'rgba(34, 197, 94, 0.05)' }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#22c55e', boxShadow: '0 0 8px #22c55e' }}></div>
                    <span style={{ color: '#22c55e', fontSize: '12px', fontWeight: 'bold' }}>Ubuntu Agent: Online</span>
                </div>

                {/* Icon Cài đặt */}
                <Settings size={20} color="#94a3b8" style={{ cursor: 'pointer' }} />

                {/* Avatar Quản trị viên */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{ background: '#1e293b', borderRadius: '50%', padding: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <User size={18} color="#cbd5e1" />
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                        <span style={{ fontSize: '13px', fontWeight: 'bold', color: '#f8fafc' }}>Admin</span>
                        <span style={{ fontSize: '11px', color: '#64748b' }}>Administrator</span>
                    </div>
                </div>
            </div>
        </header>
    );
}