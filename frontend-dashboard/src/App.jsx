import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import History from './pages/History';
import Login from './pages/Login';
import Account from './pages/Account';
import Settings from './pages/Settings';
import PcapAnalysis from './pages/PcapAnalysis';

function AppRoutes() {
    const { isAuthenticated } = useAuth();

    return (
        <Routes>
            <Route 
                path="/login" 
                element={!isAuthenticated ? <Login onLoginSuccess={() => window.location.href='/dashboard'} /> : <Navigate to="/dashboard" />} 
            />
            
            <Route path="/dashboard" element={isAuthenticated ? <MainLayout><Dashboard /></MainLayout> : <Navigate to="/login" />} />
            <Route path="/pcap" element={isAuthenticated ? <MainLayout><PcapAnalysis /></MainLayout> : <Navigate to="/login" />} />
            <Route path="/history" element={isAuthenticated ? <MainLayout><History /></MainLayout> : <Navigate to="/login" />} />
            <Route path="/account" element={isAuthenticated ? <MainLayout><Account /></MainLayout> : <Navigate to="/login" />} />
            <Route path="/settings" element={isAuthenticated ? <MainLayout><Settings /></MainLayout> : <Navigate to="/login" />} />
            
            <Route path="*" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />} />
        </Routes>
    );
}

export default function App() {
    return (
        <AuthProvider>
            <Router>
                <AppRoutes />
            </Router>
        </AuthProvider>
    );
}
