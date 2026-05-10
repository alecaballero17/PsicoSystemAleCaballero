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
        onClose();
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
            <aside className={`global-sidebar ${isOpen ? 'open' : ''}`}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        {tenant?.logo ? (
                            <img src={tenant.logo} alt="Tenant Logo" style={{ width: '40px', height: '40px', borderRadius: '8px', objectFit: 'cover' }} />
                        ) : (
                            <div style={{ width: '32px', height: '32px', backgroundColor: '#3b82f6', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px' }}>
                                🏥
                            </div>
                        )}
                        <span style={{ fontWeight: '800', fontSize: '18px', color: 'white' }}>
                            {tenant?.nombre?.toUpperCase() || 'PSICOSYSTEM'}
                        </span>
                    </div>
                    <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: 'white', fontSize: '24px', cursor: 'pointer' }}>×</button>
                </div>
                
                {/* Buscador de Módulos */}
                <div style={{ marginBottom: '24px' }}>
                    <input 
                        type="text" 
                        placeholder="🔍 Buscar módulo..." 
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        style={{
                            width: '100%', padding: '10px 14px', borderRadius: '10px', 
                            border: '1px solid #334155', backgroundColor: '#1e293b', 
                            color: 'white', fontSize: '13px', outline: 'none', boxSizing: 'border-box'
                        }}
                    />
                </div>

                <div style={{ overflowY: 'auto', flex: 1 }}>
                    {/* Sección Principal */}
                    <nav className="navSection">
                        <p className="sectionLabel">PRINCIPAL</p>
                        {matchesSearch('Vista General Analítica') && (
                            <div className="navItem" onClick={() => handleNavigate('/dashboard')}>📊 Vista General Analítica</div>
                        )}
                        {matchesSearch('Agenda Profesional') && (
                            <div className="navItem" onClick={() => handleNavigate('/agenda')}>📅 Agenda Profesional</div>
                        )}
                        {matchesSearch('Gestión de Citas') && (
                            <div className="navItem" onClick={() => handleNavigate('/gestion-citas')}>🗓️ Gestión de Citas</div>
                        )}
                    </nav>

                    {/* Sección Clínica */}
                    {(userRole === 'PSICOLOGO' || userRole === 'ADMIN') && (
                        <nav className="navSection">
                            <p className="sectionLabel">CLÍNICA</p>
                            {matchesSearch('Registro de Pacientes') && (
                                <div className="navItem" onClick={() => handleNavigate('/registro-paciente')}>📋 Registro de Pacientes</div>
                            )}
                            {matchesSearch('Historia Clínica IA') && (
                                <div className="navItem" onClick={() => handleNavigate('/historia-clinica')}>🏥 Historia Clínica + IA</div>
                            )}
                            {matchesSearch('Lista de Espera') && (
                                <div className="navItem" onClick={() => handleNavigate('/lista-espera')}>⏳ Lista de Espera</div>
                            )}
                            {matchesSearch('Escáner QR Citas') && (
                                <div className="navItem" onClick={() => handleNavigate('/escaner-qr')}>📷 Escáner QR de Citas</div>
                            )}
                        </nav>
                    )}

                    {/* Sección Financiera */}
                    {(userRole === 'PSICOLOGO' || userRole === 'ADMIN') && (
                        <nav className="navSection">
                            <p className="sectionLabel">FINANZAS</p>
                            {matchesSearch('Módulo Financiero') && (
                                <div className="navItem" onClick={() => handleNavigate('/finanzas')}>💰 Módulo Financiero</div>
                            )}
                            {userRole === 'ADMIN' && matchesSearch('Reportes Económicos') && (
                                <div className="navItem" onClick={() => handleNavigate('/reportes')}>📊 Reportes Económicos</div>
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
                            {matchesSearch('Configuración Clínica') && (
                                <div className="navItem" onClick={() => handleNavigate('/configuracion-clinica')}>⚙️ Configuración de Clínica</div>
                            )}
                            {matchesSearch('Suscripción SaaS') && (
                                <div className="navItem" onClick={() => handleNavigate('/suscripcion')}>💎 Suscripción SaaS</div>
                            )}
                        </nav>
                    )}
                </div>

                {/* Footer */}
                <div style={{ marginTop: 'auto', paddingTop: '24px', borderTop: '1px solid #1e293b' }}>
                    <button 
                        onClick={async () => { 
                            onClose();
                            await logout(); 
                            navigate('/'); 
                        }} 
                        style={{
                            width: '100%', padding: '12px', backgroundColor: '#ef444415', 
                            color: '#ef4444', border: 'none', borderRadius: '12px', 
                            cursor: 'pointer', fontWeight: '600'
                        }}
                    >
                        Finalizar Sesión
                    </button>
                </div>
            </aside>
        </>
    );
};

export default GlobalSidebar;
