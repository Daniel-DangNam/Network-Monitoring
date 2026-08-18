import { useState } from 'react';
import { loginUser } from '../services/api';
import { Shield, User, Lock, Eye, EyeOff, ShieldCheck } from 'lucide-react';

export default function Login({ onLoginSuccess }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    
    // State quản lý ẩn/hiện mật khẩu
    const [showPassword, setShowPassword] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);
        try {
            const data = await loginUser(username, password);
            localStorage.setItem('token', data.access_token);
            onLoginSuccess();
        } catch {
            setError('Tài khoản hoặc mật khẩu không chính xác!');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div style={{ height: '100vh', width: '100vw', display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#050b14', color: '#e2e8f0', backgroundImage: 'radial-gradient(circle at center, #0a192f 0%, #050b14 100%)' }}>
            
            <form onSubmit={handleSubmit} style={{ 
                background: '#0f172a', 
                padding: '40px 30px', 
                borderRadius: '16px', 
                width: '400px', 
                border: '1px solid #0ea5e9', 
                boxShadow: '0 0 20px rgba(14, 165, 233, 0.15), inset 0 0 10px rgba(14, 165, 233, 0.05)' 
            }}>
                
                {/* Khu vực Header */}
                <div style={{ textAlign: 'center', marginBottom: '30px' }}>
                    <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(14, 165, 233, 0.1)', padding: '15px', borderRadius: '50%', marginBottom: '15px', border: '1px solid rgba(14, 165, 233, 0.3)' }}>
                        <Shield size={40} color="#0ea5e9" strokeWidth={1.5} />
                    </div>
                    <h2 style={{ margin: '0 0 8px 0', color: '#f8fafc', fontSize: '22px', fontWeight: 'bold', letterSpacing: '1px' }}>
                        NETWORK <span style={{ color: '#0ea5e9' }}>AI</span> MONITOR
                    </h2>
                    <p style={{ margin: '0', color: '#94a3b8', fontSize: '13px' }}>
                        Enter your credentials to access the security portal
                    </p>
                </div>
                
                {/* Hiển thị lỗi nếu có */}
                {error && (
                    <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', padding: '10px', borderRadius: '8px', marginBottom: '20px', fontSize: '13px', border: '1px solid rgba(239, 68, 68, 0.2)', textAlign: 'center' }}>
                        {error}
                    </div>
                )}

                {/* Input Username */}
                <div style={{ marginBottom: '20px' }}>
                    <label style={{ display: 'block', marginBottom: '8px', fontSize: '13px', color: '#cbd5e1' }}>Username</label>
                    <div style={{ position: 'relative' }}>
                        <div style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#0ea5e9' }}>
                            <User size={18} />
                        </div>
                        <input 
                            type="text" 
                            value={username} 
                            onChange={(e) => setUsername(e.target.value)} 
                            required 
                            style={{ width: '100%', padding: '12px 12px 12px 40px', borderRadius: '8px', border: '1px solid #334155', background: 'rgba(15, 23, 42, 0.6)', color: '#f8fafc', boxSizing: 'border-box', outline: 'none', transition: 'border-color 0.3s' }}
                            placeholder="Enter your username"
                            onFocus={(e) => e.target.style.borderColor = '#0ea5e9'}
                            onBlur={(e) => e.target.style.borderColor = '#334155'}
                        />
                    </div>
                </div>

                {/* Input Password */}
                <div style={{ marginBottom: '20px' }}>
                    <label style={{ display: 'block', marginBottom: '8px', fontSize: '13px', color: '#cbd5e1' }}>Password</label>
                    <div style={{ position: 'relative' }}>
                        <div style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#0ea5e9' }}>
                            <Lock size={18} />
                        </div>
                        <input 
                            type={showPassword ? "text" : "password"} 
                            value={password} 
                            onChange={(e) => setPassword(e.target.value)} 
                            required 
                            style={{ width: '100%', padding: '12px 40px 12px 40px', borderRadius: '8px', border: '1px solid #334155', background: 'rgba(15, 23, 42, 0.6)', color: '#f8fafc', boxSizing: 'border-box', outline: 'none', transition: 'border-color 0.3s' }}
                            placeholder="••••••••"
                            onFocus={(e) => e.target.style.borderColor = '#0ea5e9'}
                            onBlur={(e) => e.target.style.borderColor = '#334155'}
                        />
                        <div 
                            style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', color: '#64748b', cursor: 'pointer' }}
                            onClick={() => setShowPassword(!showPassword)}
                        >
                            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                        </div>
                    </div>
                </div>

                {/* Các tùy chọn phụ */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px', fontSize: '13px' }}>
                    <label style={{ display: 'flex', alignItems: 'center', color: '#94a3b8', cursor: 'pointer' }}>
                        <input type="checkbox" style={{ marginRight: '8px', cursor: 'pointer', accentColor: '#0ea5e9' }} />
                        Remember me
                    </label>
                    <a href="#" style={{ color: '#0ea5e9', textDecoration: 'none', transition: 'color 0.3s' }} onMouseOver={(e) => e.target.style.color = '#38bdf8'} onMouseOut={(e) => e.target.style.color = '#0ea5e9'}>
                        Forgot Password?
                    </a>
                </div>

                {/* Nút Submit */}
                <button 
                    type="submit" 
                    disabled={isLoading} 
                    style={{ 
                        width: '100%', 
                        padding: '12px', 
                        background: isLoading ? '#0284c7' : 'linear-gradient(90deg, #0284c7, #0ea5e9)', 
                        color: '#fff', 
                        border: 'none', 
                        borderRadius: '8px', 
                        cursor: isLoading ? 'not-allowed' : 'pointer', 
                        fontWeight: 'bold',
                        letterSpacing: '0.5px',
                        boxShadow: '0 4px 15px rgba(14, 165, 233, 0.4)'
                    }}
                >
                    {isLoading ? 'CONNECTING...' : 'SIGN IN >'}
                </button>

                {/* Footer Security Badge */}
                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '6px', marginTop: '25px', color: '#64748b', fontSize: '12px' }}>
                    <ShieldCheck size={14} color="#0ea5e9" />
                    <span>Encrypted JWT Authentication System</span>
                </div>

            </form>
        </div>
    );
}