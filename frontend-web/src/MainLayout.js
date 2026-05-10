import React, { useState } from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import GlobalSidebar from './components/GlobalSidebar';

const MainLayout = ({ allowedRoles }) => {
    const { user } = useAuth();
    const [isSidebarOpen, setIsSidebarOpen] = useState(window.innerWidth > 768);

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
        <div className="app-layout" style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
            <Navbar onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)} />
            <div style={{ display: 'flex', flex: 1, position: 'relative' }}>
                <GlobalSidebar 
                    isOpen={isSidebarOpen} 
                    onClose={() => setIsSidebarOpen(false)} 
                />
                <main className={`app-content-wrapper ${isSidebarOpen ? 'with-sidebar' : ''}`} style={{ flex: 1 }}>
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export default MainLayout;
