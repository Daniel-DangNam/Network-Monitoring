import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';

export default function MainLayout({ children }) {
    return (
        <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', background: '#0f172a', margin: 0, fontFamily: 'sans-serif' }}>
            <Navbar />
            <div style={{ display: 'flex', flex: 1 }}>
                <Sidebar />
                <main style={{ flex: 1, padding: '24px', overflowY: 'auto' }}>
                    {children}
                </main>
            </div>
        </div>
    );
}

