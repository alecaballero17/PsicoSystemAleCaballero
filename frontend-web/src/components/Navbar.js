import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import GlobalSidebar from './GlobalSidebar';

const Navbar = ({ onToggleSidebar }) => {
    const { user, tenant, logout } = useAuth();
    const navigate = useNavigate();
    const [showDropdown, setShowDropdown] = useState(false);

    const navStyle = {
        height: '64px',
        backgroundColor: 'rgba(255, 255, 255, 0.75)',
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid rgba(226, 232, 240, 0.8)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        position: 'sticky',
        top: 0,
        zIndex: 1100,
        boxShadow: '0 4px 12px rgba(0,0,0,0.03)'
    };

    return (
        <nav style={{ ...navStyle, zIndex: 1200 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                {user && (
                <button 
                    onClick={onToggleSidebar}
                    style={{ 
                        background: '#f1f5f9', 
                        border: 'none', 
                        color: '#475569', 
                        fontSize: '20px', 
                        cursor: 'pointer', 
                        borderRadius: '10px',
                        width: '40px',
                        height: '40px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        transition: 'all 0.2s',
                        boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                    }}
                >
                    ☰
                </button>
            )}
            
            <a href="/dashboard" style={{ display: 'flex', alignItems: 'center', gap: '12px', textDecoration: 'none', color: '#1e293b' }}>
                {tenant?.logo ? (
                    <img src={tenant.logo} alt="Logo" style={{ width: '38px', height: '38px', borderRadius: '10px', objectFit: 'cover', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }} />
                ) : (
                    <div style={{ width: '38px', height: '38px', background: 'linear-gradient(135deg, #2563eb 0%, #1e40af 100%)', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '900', fontSize: '18px', boxShadow: '0 4px 6px rgba(37,99,235,0.2)' }}>
                        🏥
                    </div>
                )}
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <span style={{ margin: 0, fontSize: '15px', letterSpacing: '-0.3px', fontWeight: '900', textTransform: 'uppercase', color: '#0f172a' }}>
                            {tenant?.nombre || "PSICOSYSTEM"}
                        </span>
                        <span style={{ fontSize: '10px', color: '#94a3b8', fontWeight: '600', letterSpacing: '1px' }}>SISTEMA DE GESTIÓN</span>
                    </div>
                </a>
            </div>
            
            {user && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                    <div style={{ position: 'relative' }}>
                        <button 
                            onClick={() => setShowDropdown(!showDropdown)}
                            className="profile-btn-hover"
                            style={{ 
                                display: 'flex', alignItems: 'center', gap: '12px',
                                background: 'white', border: '1px solid #e2e8f0', padding: '6px 16px 6px 8px',
                                borderRadius: '30px', color: '#1e293b', cursor: 'pointer',
                                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)', 
                                boxShadow: showDropdown ? '0 0 0 3px rgba(37,99,235,0.1)' : '0 4px 6px -1px rgba(0,0,0,0.05)',
                                outline: 'none'
                            }}
                        >
                            <div style={{ 
                                width: '32px', height: '32px', borderRadius: '50%', 
                                background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)', 
                                display: 'flex', alignItems: 'center', justifyContent: 'center', 
                                color: 'white', fontWeight: '800', fontSize: '13px',
                                boxShadow: '0 2px 4px rgba(37,99,235,0.3)'
                            }}>
                                {user?.username?.[0]?.toUpperCase()}
                            </div>
                            <div style={{ textAlign: 'left' }}>
                                <p style={{ margin: 0, fontSize: '12px', fontWeight: '800', lineHeight: 1 }}>{user?.username?.toUpperCase()}</p>
                                <p style={{ margin: 0, fontSize: '10px', color: '#64748b', fontWeight: '600' }}>{user?.role}</p>
                            </div>
                            <span style={{ fontSize: '10px', transition: 'transform 0.3s', transform: showDropdown ? 'rotate(180deg)' : 'rotate(0)' }}>▼</span>
                        </button>

                        {showDropdown && (
                            <div style={{
                                position: 'absolute', top: '55px', right: 0,
                                width: '280px', backgroundColor: 'white', borderRadius: '16px',
                                boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04)',
                                border: '1px solid #f1f5f9',
                                padding: '8px', zIndex: 1200, color: '#1e293b',
                                animation: 'slideIn 0.2s ease-out'
                            }}>
                                <div style={{ padding: '12px 16px', borderBottom: '1px solid #f1f5f9', marginBottom: '8px' }}>
                                    <p style={{ margin: 0, fontSize: '11px', color: '#64748b', fontWeight: '800', letterSpacing: '0.5px' }}>GESTIÓN DE CUENTA</p>
                                </div>
                                
                                {user?.role === 'ADMIN' && (
                                    <>
                                        <button onClick={() => { navigate('/suscripcion'); setShowDropdown(false); }} style={styles.dropdownItem}>💎 Suscripción SaaS</button>
                                        <button onClick={() => { navigate('/configuracion-clinica'); setShowDropdown(false); }} style={styles.dropdownItem}>⚙️ Configuración de Clínica</button>
                                        <button onClick={() => { navigate('/facturacion'); setShowDropdown(false); }} style={styles.dropdownItem}>💰 Historial de Facturación</button>
                                        <button onClick={() => { navigate('/escaner-qr'); setShowDropdown(false); }} style={styles.dropdownItem}>📷 Escáner QR de Citas</button>
                                        <div style={{ height: '1px', background: '#f1f5f9', margin: '8px 0' }}></div>
                                    </>
                                )}
                                
                                <button onClick={() => { navigate('/bitacora'); setShowDropdown(false); }} style={styles.dropdownItem}>📜 Bitácora de Auditoría</button>
                                <button onClick={() => { navigate('/cambiar-password'); setShowDropdown(false); }} style={styles.dropdownItem}>🔐 Cambiar Contraseña</button>
                                
                                <div style={{ borderTop: '1px solid #f1f5f9', marginTop: '8px', paddingTop: '8px' }}>
                                    <button onClick={async () => {
                                        setShowDropdown(false);
                                        await logout();
                                        navigate('/');
                                    }} style={{ 
                                        ...styles.dropdownItem, 
                                        color: '#ef4444', 
                                        fontWeight: '800',
                                        backgroundColor: '#fef2f2',
                                        marginTop: '4px'
                                    }}>🚪 Cerrar Sesión</button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}
            <style>{`
                @keyframes slideIn {
                    from { opacity: 0; transform: translateY(-10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                .profile-btn-hover:hover {
                    background-color: #f8fafc !important;
                    transform: translateY(-1px);
                    box-shadow: 0 6px 12px -1px rgba(0,0,0,0.1) !important;
                }
                .profile-btn-hover:active {
                    transform: translateY(0);
                }
            `}</style>
        </nav>
    );
};

const styles = {
    dropdownItem: {
        width: '100%', padding: '10px 12px', backgroundColor: 'transparent',
        border: 'none', textAlign: 'left', cursor: 'pointer', fontSize: '13px',
        color: '#334155', fontWeight: '700', borderRadius: '8px',
        transition: 'all 0.2s', display: 'flex', alignItems: 'center', gap: '10px'
    }
};

export default Navbar;