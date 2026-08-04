import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import History from './pages/History';
import Login from './pages/Login';
import Account from './pages/Account';
import Settings from './pages/Settings';
import Sidebar from './components/Sidebar';

export default function App() {
    const isAuthenticated = !!localStorage.getItem('token');

    return (
        <Router>
            {/* Đổi màu background tổng thể thành Dark Blue (#0f172a) */}
            <div style={{ display: 'flex', minHeight: '100vh', background: '#0f172a', margin: 0, fontFamily: 'sans-serif' }}>
                {isAuthenticated && <Sidebar />}
                
                <div style={{ flex: 1, overflowX: 'hidden' }}>
                    <Routes>
                        <Route path="/login" element={!isAuthenticated ? <Login onLoginSuccess={() => window.location.href='/dashboard'} /> : <Navigate to="/dashboard" />} />
                        
                        <Route path="/dashboard" element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" />} />
                        <Route path="/history" element={isAuthenticated ? <History /> : <Navigate to="/login" />} />
                        <Route path="/account" element={isAuthenticated ? <Account /> : <Navigate to="/login" />} />
                        <Route path="/settings" element={isAuthenticated ? <Settings /> : <Navigate to="/login" />} />
                        
                        <Route path="*" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />} />
                    </Routes>
                </div>
            </div>
        </Router>
    );
}