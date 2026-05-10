import React, { useState } from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import GlobalSidebar from './components/GlobalSidebar';

const MainLayout = ({ allowedRoles }) => {
    const { user } = useAuth();
    const [isSidebarOpen, setIsSidebarOpen] = useState(() => {
        if (window.innerWidth <= 768) return false;
        const saved = localStorage.getItem('sidebarOpen');
        return saved !== null ? JSON.parse(saved) : true;
    });

    const toggleSidebar = () => {
        const newState = !isSidebarOpen;
        setIsSidebarOpen(newState);
        localStorage.setItem('sidebarOpen', JSON.stringify(newState));
    };

    const closeSidebar = () => {
        if (window.innerWidth <= 768) {
            setIsSidebarOpen(false);
        }
    };

    React.useEffect(() => {
        const handleResize = () => {
            if (window.innerWidth <= 768 && isSidebarOpen) {
                setIsSidebarOpen(false);
            }
        };
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, [isSidebarOpen]);

    if (!user) {
        return <Navigate to="/" />;
    }

    if (user && (!user.clinica_id || user.clinica_id === "null" || user.clinica_id === "undefined") && user.role !== 'PACIENTE') {
        return <Navigate to="/registro-clinica" />;
    }

    if (allowedRoles && !allowedRoles.includes(user.role)) {
        return <Navigate to="/dashboard" />;
    }

    return (
        <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', backgroundColor: '#f1f5f9' }}>
            <Navbar onToggleSidebar={toggleSidebar} />
            
            <div style={{ display: 'flex', flex: 1, position: 'relative' }}>
                <GlobalSidebar isOpen={isSidebarOpen} onClose={closeSidebar} />
                
                <main style={{ 
                    flex: 1,
                    marginLeft: (isSidebarOpen && window.innerWidth > 768) ? '280px' : '0',
                    transition: 'margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    width: '100%',
                    padding: '0',
                    boxSizing: 'border-box',
                    minHeight: 'calc(100vh - 64px)'
                }}>
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export default MainLayout;
