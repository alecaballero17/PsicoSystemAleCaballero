// ==============================================================================
// [SPRINT 1 + SPRINT 2] Dashboard — Panel de Control Principal
// KPIs en tiempo real, navegación por módulos, tabla de expedientes.
// ==============================================================================
import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import dashboardService from '../services/dashboardService';
import pacienteService from '../services/pacienteService';
import { dashboardStyles as styles } from '../styles/dashboardStyles';
import { useAuth } from '../context/AuthContext';
import './Dashboard.css'; // Añadimos esto para manejar media queries específicas del dashboard

const Dashboard = () => {
    const navigate = useNavigate();
    const { user, tenant, logout } = useAuth();
    
    const [pacientes, setPacientes] = useState([]);
    const [metrics, setMetrics] = useState({ total_pacientes: 0, citas_hoy: 0 });
    const [cargando, setCargando] = useState(true);
    
    // --- ESTADOS RESPONSIVES Y DE BÚSQUEDA ---
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    
    const userName = user?.name || 'USUARIO';
    const userRole = user?.role || 'ADMIN';
    const token = user?.token;

    const fetchData = useCallback(async () => {
        if (!token) {
            navigate('/');
            return;
        }

        try {
            setCargando(true);
            
            const [listaPacientes, metricasData] = await Promise.all([
                pacienteService.getPacientes(),
                dashboardService.getMetrics()
            ]);
            
            setPacientes(Array.isArray(listaPacientes) ? listaPacientes : []);
            
            const datosCrudos = metricasData.metricas || metricasData;
            setMetrics({
                total_pacientes: datosCrudos.total_pacientes || 0,
                citas_hoy: datosCrudos.citas_pendientes || 0
            });

            setCargando(false);

        } catch (error) {
            console.error("Error cargando datos de Django:", error.response?.data || error.message);
            setCargando(false);
            
            if (error.response?.status === 403) {
                const mensajeError = error.response.data.detail || "Error de permisos. Contacte al administrador.";
                alert(`⚠️ ALERTA DE SEGURIDAD\n\n${mensajeError}`);
            }
            
            if (error.response?.status === 401) {
                logout();
            }
        }
    }, [navigate, token, logout]);

    const handleDeletePaciente = async (id, nombre) => {
        if (window.confirm(`⚠️ CONFIRMACIÓN DE AUDITORÍA (RF-30)\n\n¿Está seguro de dar de baja al paciente "${nombre}"? \n\nEsta acción quedará registrada en el historial clínico para futuras auditorías.`)) {
            try {
                await authService.apiClient.delete(`pacientes/${id}/`);
                alert("Paciente dado de baja exitosamente.");
                fetchData();
            } catch (error) {
                console.error("Error al dar de baja:", error);
                alert("No se pudo completar la acción. Verifique sus permisos de administrador.");
            }
        }
    };

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const matchesSearch = (text) => text.toLowerCase().includes(searchTerm.toLowerCase());

    return (
        <div style={styles.layout} className="dashboard-layout">
            {/* OVERLAY PARA CERRAR EL MENÚ EN MÓVILES */}
            <div 
                className={`sidebar-overlay ${isSidebarOpen ? 'open' : ''}`}
                onClick={() => setIsSidebarOpen(false)}
            ></div>

            {/* SIDEBAR: Navegación Lateral */}
            <aside style={styles.sidebar} className={`dashboard-sidebar ${isSidebarOpen ? 'open' : ''}`}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                    <div style={styles.brandContainer}>
                    {tenant.logo ? (
                        <img src={tenant.logo} alt="Tenant Logo" style={{ width: '40px', height: '40px', borderRadius: '8px', objectFit: 'cover' }} />
                    ) : (
                        <div style={styles.brandLogo}>
                            <span style={{ fontSize: '20px' }}>🏥</span>
                        </div>
                    )}
                    <span style={styles.brandText}>
                        {tenant.nombre?.toUpperCase() || 'PSICOSYSTEM'} <span style={styles.brandVersion}>v2.0.0</span>
                    </span>
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

                {/* Sección Principal */}
                <nav style={styles.navSection}>
                    <p style={styles.sectionLabel}>PRINCIPAL</p>
                    {matchesSearch('Vista General Analítica') && <div style={styles.navItemActive}>📊 Vista General Analítica</div>}
                    
                    {/* Sprint 2: Agenda y Citas */}
                    {matchesSearch('Agenda Profesional') && (
                        <div style={styles.navItem} onClick={() => navigate('/agenda')}>
                            📅 Agenda Profesional
                        </div>
                    )}
                    {matchesSearch('Gestión de Citas') && (
                        <div style={styles.navItem} onClick={() => navigate('/gestion-citas')}>
                            🗓️ Gestión de Citas
                        </div>
                    )}
                </nav>

                {/* Sección Clínica (Psicólogo + Admin) */}
                {(userRole === 'PSICOLOGO' || userRole === 'ADMIN') && (
                    <nav style={styles.navSection}>
                        <p style={styles.sectionLabel}>CLÍNICA</p>
                        {matchesSearch('Registro de Pacientes') && (
                            <div style={styles.navItem} onClick={() => navigate('/registro-paciente')}>
                                📋 Registro de Pacientes
                            </div>
                        )}
                        {matchesSearch('Historia Clínica IA') && (
                            <div style={styles.navItem} onClick={() => navigate('/historia-clinica')}>
                                🏥 Historia Clínica + IA
                            </div>
                        )}
                        {matchesSearch('Lista de Espera') && (
                            <div style={styles.navItem} onClick={() => navigate('/lista-espera')}>
                                ⏳ Lista de Espera
                            </div>
                        )}
                        {matchesSearch('Escáner QR Citas') && (
                            <div style={styles.navItem} onClick={() => navigate('/escaner-qr')}>
                                📷 Escáner QR de Citas
                            </div>
                        )}
                    </nav>
                )}

                {/* Sección Financiera */}
                {(userRole === 'PSICOLOGO' || userRole === 'ADMIN') && (
                    <nav style={styles.navSection}>
                        <p style={styles.sectionLabel}>FINANZAS</p>
                        {matchesSearch('Módulo Financiero') && (
                            <div style={styles.navItem} onClick={() => navigate('/finanzas')}>
                                💰 Módulo Financiero
                            </div>
                        )}
                        {userRole === 'ADMIN' && matchesSearch('Reportes Económicos') && (
                            <div style={styles.navItem} onClick={() => navigate('/reportes')}>
                                📊 Reportes Económicos
                            </div>
                        )}
                    </nav>
                )}

                {/* Sección Administración (Solo Admin) */}
                {userRole === 'ADMIN' && (
                    <nav style={styles.navSection}>
                        <p style={styles.sectionLabel}>ADMINISTRACIÓN</p>
                        {matchesSearch('Gestión de Personal') && (
                            <div style={styles.navItem} onClick={() => navigate('/gestion-personal')}>
                                👥 Gestión de Personal
                            </div>
                        )}
                        {matchesSearch('Configuración Clínica') && (
                            <div style={styles.navItem} onClick={() => navigate('/configuracion-clinica')}>
                                ⚙️ Configuración de Clínica
                            </div>
                        )}
                        {matchesSearch('Suscripción SaaS') && (
                            <div style={styles.navItem} onClick={() => navigate('/suscripcion')}>
                                💎 Suscripción SaaS
                            </div>
                        )}
                    </nav>
                )}

                {/* Footer */}
                <div style={styles.sidebarFooter}>
                    <div style={{ paddingBottom: '15px', borderBottom: '1px solid rgba(255,255,255,0.1)', marginBottom: '15px' }}>
                        <div style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '5px' }}>
                            🏥 SESIÓN INICIADA EN:
                        </div>
                        <div style={{ fontSize: '13px', color: 'white', fontWeight: 'bold' }}>
                            {tenant?.nombre || "Cargando Clínica..."}
                        </div>
                    </div>
                    <div style={styles.sessionInfo}>
                        <div style={styles.statusDot}></div>
                        <span>Servidor: Online</span>
                    </div>
                    <button 
                        onClick={async () => { 
                            await authService.logout(); 
                            logout(); 
                            navigate('/'); 
                        }} 
                        style={styles.logoutBtn}
                    >
                        Finalizar Sesión
                    </button>
                </div>
            </aside>

            {/* MAIN CONTENT */}
            <main style={styles.main}>
                <header style={styles.header}>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                        <div style={styles.headerPath}>Consola / Dashboard</div>
                    </div>
                    <div className="header-user-info" style={{ ...styles.headerUser, display: 'flex', flexDirection: 'column', alignItems: 'flex-end', justifyContent: 'center' }}>
                        <span style={{ color: '#1e293b', fontSize: '14px', fontWeight: '800', marginBottom: '4px' }}>
                            🏥 {tenant?.nombre || "Cargando Clínica..."}
                        </span>
                        <div>
                            <span style={styles.userRoleTag}>{userRole}</span>
                            <span style={styles.userName}>{userName}</span>
                        </div>
                    </div>
                </header>

                <div style={styles.content}>
                    {/* KPIs */}
                    <div style={styles.kpiGrid} className="kpi-grid">
                        <div style={styles.kpiCard}>
                            <span style={styles.kpiLabel}>TOTAL PACIENTES</span>
                            <div style={styles.kpiValue}>{metrics.total_pacientes}</div>
                            <div style={styles.kpiSub}>Sincronizado con PostgreSQL</div>
                        </div>
                        <div style={styles.kpiCard}>
                            <span style={styles.kpiLabel}>CITAS PENDIENTES</span>
                            <div style={styles.kpiValue}>{metrics.citas_hoy}</div>
                            <div style={{ ...styles.kpiSub, cursor: 'pointer' }} onClick={() => navigate('/agenda')}>
                                Ver en Agenda →
                            </div>
                        </div>
                        <div style={styles.kpiCard}>
                            <span style={styles.kpiLabel}>ESTADO API</span>
                            <div style={styles.kpiValue}>ONLINE</div>
                            <div style={styles.kpiSub}>Sprint 2 — v2.0.0</div>
                        </div>
                    </div>

                    {/* Sprint 2 Quick Actions */}
                    <div className="quick-actions-grid" style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(5, 1fr)',
                        gap: '16px',
                        marginBottom: '32px',
                    }}>
                        <div onClick={() => navigate('/gestion-citas')} style={quickActionStyle}>
                            <span style={{ fontSize: '28px' }}>🗓️</span>
                            <span style={{ fontWeight: '700', color: '#0f172a', fontSize: '13px' }}>Nueva Cita</span>
                        </div>
                        <div onClick={() => navigate('/historia-clinica')} style={quickActionStyle}>
                            <span style={{ fontSize: '28px' }}>📋</span>
                            <span style={{ fontWeight: '700', color: '#0f172a', fontSize: '13px' }}>Expedientes</span>
                        </div>
                        <div onClick={() => navigate('/finanzas')} style={quickActionStyle}>
                            <span style={{ fontSize: '28px' }}>💰</span>
                            <span style={{ fontWeight: '700', color: '#0f172a', fontSize: '13px' }}>Registrar Pago</span>
                        </div>
                        <div onClick={() => navigate('/lista-espera')} style={quickActionStyle}>
                            <span style={{ fontSize: '28px' }}>⏳</span>
                            <span style={{ fontWeight: '700', color: '#0f172a', fontSize: '13px' }}>Lista Espera</span>
                        </div>
                        <div onClick={() => navigate('/escaner-qr')} style={quickActionStyle}>
                            <span style={{ fontSize: '28px' }}>📷</span>
                            <span style={{ fontWeight: '700', color: '#0f172a', fontSize: '13px' }}>Escanear QR</span>
                        </div>
                    </div>

                    {/* Tabla de Pacientes */}
                    <div style={styles.panelSection}>
                        <div style={styles.panelHeader}>
                            <h3 style={styles.panelTitle}>EXPEDIENTES RECIENTES (TRAZABILIDAD T014)</h3>
                            {userRole !== 'PACIENTE' && (
                                <button 
                                    onClick={() => navigate('/registro-paciente')} 
                                    style={styles.mainActionBtn}
                                >
                                    + NUEVO REGISTRO
                                </button>
                            )}
                        </div>
                        
                        <div style={styles.tableContainer}>
                            <table style={styles.table}>
                                <thead>
                                    <tr style={styles.tableHeader}>
                                        <th style={styles.th}>ID</th>
                                        <th style={styles.th}>PACIENTE</th>
                                        <th style={styles.th}>IDENTIFICACIÓN</th>
                                        <th style={styles.th}>ESTADO</th>
                                        {userRole === 'ADMIN' && <th style={{ ...styles.th, textAlign: 'right' }}>ACCIONES</th>}
                                    </tr>
                                </thead>
                                <tbody>
                                    {pacientes.length > 0 ? (
                                        pacientes.map((p) => (
                                            <tr key={p.id} style={styles.tableRow}>
                                                <td style={styles.td}>#{p.id}</td>
                                                <td style={styles.tdBold}>
                                                    {(p.nombre || "PACIENTE SIN NOMBRE").toUpperCase()}
                                                    {p.origen === 'MOVIL' && (
                                                        <span style={{
                                                            marginLeft: '8px', 
                                                            fontSize: '10px', 
                                                            backgroundColor: '#3b82f6', 
                                                            color: 'white', 
                                                            padding: '2px 6px', 
                                                            borderRadius: '10px',
                                                            verticalAlign: 'middle'
                                                        }}>📱 MÓVIL</span>
                                                    )}
                                                </td>
                                                <td style={styles.td}>{p.ci || p.identificacion || 'S/N'}</td>
                                                <td style={styles.td}>
                                                    <span style={styles.statusActive}>ACTIVO</span>
                                                </td>
                                                {userRole === 'ADMIN' && (
                                                    <td style={{ textAlign: 'right', padding: '16px' }}>
                                                        <button 
                                                            title="Dar de baja (Admin Only)"
                                                            style={styles.btnDeleteBase}
                                                            onClick={() => handleDeletePaciente(p.id, p.nombre)}
                                                        >
                                                            🗑️
                                                        </button>
                                                    </td>
                                                )}
                                            </tr>
                                        ))
                                    ) : (
                                        <tr>
                                            <td colSpan="4" style={{padding: '40px', textAlign: 'center', color: '#64748b'}}>
                                                {cargando 
                                                    ? "Consultando base de datos PostgreSQL..." 
                                                    : "No hay pacientes registrados para este Tenant."}
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                        <p style={styles.technicalNote}>
                            * Datos aislados mediante arquitectura Multi-tenant (RF-29).
                        </p>
                    </div>
                </div>
            </main>
        </div>
    );
};

// Quick Action Card Style
const quickActionStyle = {
    backgroundColor: 'white',
    borderRadius: '16px',
    border: '1px solid #e2e8f0',
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '10px',
    cursor: 'pointer',
    transition: 'all 0.2s',
    boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
};

export default Dashboard;