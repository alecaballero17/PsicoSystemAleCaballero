import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './GlobalSidebar.css';

const GlobalSidebar = ({ isOpen, onClose }) => {
    const navigate = useNavigate();
    const { user, tenant, logout } = useAuth();
    const [searchTerm, setSearchTerm] = useState('');

    const userRole = user?.role || 'ADMIN';
    const matchesSearch = (text) => text.toLowerCase().includes(searchTerm.toLowerCase());

    const handleNavigate = (path) => {
        if (window.innerWidth <= 768) {
            onClose();
        }
        navigate(path);
    };

    return (
        <>
            {/* Overlay para cerrar haciendo clic afuera */}
            <div 
                className={`global-sidebar-overlay ${isOpen ? 'open' : ''}`}
                onClick={onClose}
            ></div>

            {/* Panel Lateral */}
            <aside className={`global-sidebar ${isOpen ? 'open' : ''}`} style={{ paddingTop: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        {tenant?.logo ? (
                            <img src={tenant.logo} alt="Logo" style={{ width: '40px', height: '40px', borderRadius: '10px', objectFit: 'cover' }} />
                        ) : (
                            <div style={{ width: '40px', height: '40px', backgroundColor: '#3b82f6', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '22px' }}>🧠</div>
                        )}
                        <span style={{ fontWeight: '900', color: 'white', fontSize: '16px', letterSpacing: '0.5px' }}>PSICOSYSTEM</span>
                    </div>
                    <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: '#64748b', fontSize: '20px', cursor: 'pointer' }}>✕</button>
                </div>
                
                <div style={{ padding: '15px 0 25px 0', borderBottom: '1px solid #1e293b', marginBottom: '20px' }}>
                    <p style={{ color: '#3b82f6', fontSize: '10px', fontWeight: '900', letterSpacing: '2px', margin: '0 0 8px 0', opacity: 0.8 }}>TENANT ACTIVO</p>
                    <h3 style={{ margin: 0, fontSize: '17px', color: 'white', fontWeight: '900', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {tenant?.nombre || 'MI CLÍNICA'}
                    </h3>
                </div>
                
                {/* Buscador de Módulos */}
                <div style={{ marginBottom: '24px' }}>
                    <div style={{ position: 'relative' }}>
                        <input 
                            type="text" 
                            placeholder="Buscar módulo..." 
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            style={{
                                width: '100%', padding: '12px 14px 12px 35px', borderRadius: '12px', 
                                border: '1px solid #334155', backgroundColor: '#1e293b', 
                                color: 'white', fontSize: '13px', outline: 'none', boxSizing: 'border-box'
                            }}
                        />
                        <span style={{ position: 'absolute', left: '12px', top: '12px', opacity: 0.5 }}>🔍</span>
                    </div>
                </div>

                <div className="sidebar-scroll-container" style={{ overflowY: 'auto', flex: 1, paddingRight: '5px' }}>
                    {/* Sección Principal */}
                    <nav className="navSection">
                        <p className="sectionLabel">PANEL DE CONTROL</p>
                        {matchesSearch('Vista General Analítica') && (
                            <div className="navItem" onClick={() => handleNavigate('/dashboard')}>📊 Dashboard</div>
                        )}
                        {matchesSearch('Agenda Profesional') && (
                            <div className="navItem" onClick={() => handleNavigate('/agenda')}>📅 Agenda</div>
                        )}
                        {matchesSearch('Gestión de Citas') && (
                            <div className="navItem" onClick={() => handleNavigate('/gestion-citas')}>🗓️ Citas</div>
                        )}
                    </nav>

                    {/* Sección Clínica */}
                    {(userRole === 'PSICOLOGO' || userRole === 'ADMIN') && (
                        <nav className="navSection">
                            <p className="sectionLabel">MÓDULOS CLÍNICOS</p>
                            {matchesSearch('Registro de Pacientes') && (
                                <div className="navItem" onClick={() => handleNavigate('/registro-paciente')}>👤 Pacientes</div>
                            )}
                            {matchesSearch('Historia Clínica IA') && (
                                <div className="navItem" onClick={() => handleNavigate('/historia-clinica')}>🏥 Historias + IA</div>
                            )}
                            {matchesSearch('Lista de Espera') && (
                                <div className="navItem" onClick={() => handleNavigate('/lista-espera')}>⏳ Espera</div>
                            )}
                        </nav>
                    )}

                    {/* Sección Financiera */}
                    {(userRole === 'PSICOLOGO' || userRole === 'ADMIN') && (
                        <nav className="navSection">
                            <p className="sectionLabel">ADMIN. FINANCIERA</p>
                            {matchesSearch('Módulo Financiero') && (
                                <div className="navItem" onClick={() => handleNavigate('/finanzas')}>💰 Finanzas</div>
                            )}
                            {userRole === 'ADMIN' && matchesSearch('Reportes Económicos') && (
                                <div className="navItem" onClick={() => handleNavigate('/reportes')}>📊 Reportes</div>
                            )}
                        </nav>
                    )}

                    {/* Sección Administración */}
                    {userRole === 'ADMIN' && (
                        <nav className="navSection">
                            <p className="sectionLabel">ADMINISTRACIÓN</p>
                            {matchesSearch('Gestión de Personal') && (
                                <div className="navItem" onClick={() => handleNavigate('/gestion-personal')}>👥 Gestión de Personal</div>
                            )}
                        </nav>
                    )}
                </div>

                {/* Footer User Card */}
                <div style={{ marginTop: 'auto', paddingTop: '20px', borderTop: '1px solid #1e293b' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '15px', padding: '0 5px' }}>
                        <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: '#2563eb', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px', fontWeight: 'bold' }}>
                            {user?.username?.[0]?.toUpperCase()}
                        </div>
                        <div style={{ overflow: 'hidden' }}>
                            <p style={{ margin: 0, fontSize: '13px', fontWeight: '700', color: 'white', whiteSpace: 'nowrap', textOverflow: 'ellipsis' }}>{user?.first_name || user?.username}</p>
                            <p style={{ margin: 0, fontSize: '10px', color: '#64748b', fontWeight: '600' }}>{userRole}</p>
                        </div>
                    </div>
                    <button 
                        onClick={async () => { 
                            onClose();
                            await logout(); 
                            navigate('/'); 
                        }} 
                        style={{
                            width: '100%', padding: '12px', backgroundColor: '#ef444420', 
                            color: '#ef4444', border: 'none', borderRadius: '12px', 
                            cursor: 'pointer', fontWeight: '800', fontSize: '13px',
                            transition: 'all 0.2s'
                        }}
                        onMouseOver={(e) => e.target.style.backgroundColor = '#ef444430'}
                        onMouseOut={(e) => e.target.style.backgroundColor = '#ef444420'}
                    >
                        Cerrar Sesión
                    </button>
                </div>
            </aside>
        </>
    );
};

export default GlobalSidebar;
