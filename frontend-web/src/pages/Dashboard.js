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
        <div style={{ ...styles.content, backgroundColor: '#f8fafc', minHeight: '100vh' }}>
            {/* Welcome Premium Section */}
            <div style={{
                marginBottom: '40px',
                padding: '32px',
                borderRadius: '24px',
                background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
                color: 'white',
                boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)',
                position: 'relative',
                overflow: 'hidden'
            }}>
                <div style={{ position: 'relative', zIndex: 1 }}>
                    <p style={{ margin: 0, fontSize: '14px', fontWeight: '600', opacity: 0.7, letterSpacing: '1px' }}>RESUMEN OPERATIVO</p>
                    <h1 style={{ margin: '8px 0', fontSize: '32px', fontWeight: '900', letterSpacing: '-1px' }}>
                        ¡Hola, {userName.split(' ')[0]}! 👋
                    </h1>
                    <p style={{ margin: 0, fontSize: '16px', fontWeight: '500', opacity: 0.9 }}>
                        Gestionando <span style={{ color: '#3b82f6', fontWeight: '800' }}>{tenant?.nombre || 'tu clínica'}</span> en el Plan {tenant?.plan_suscripcion || 'SaaS'}
                    </p>
                </div>
                {/* Decoración abstracta */}
                <div style={{ position: 'absolute', right: '-50px', top: '-50px', width: '200px', height: '200px', borderRadius: '50%', background: 'rgba(59, 130, 246, 0.1)', filter: 'blur(40px)' }}></div>
                <div style={{ position: 'absolute', right: '100px', bottom: '-50px', width: '150px', height: '150px', borderRadius: '50%', background: 'rgba(37, 99, 235, 0.1)', filter: 'blur(40px)' }}></div>
            </div>

            {/* KPIs Grid */}
            <div style={styles.kpiGrid} className="kpi-grid">
                <div style={{ ...styles.kpiCard, borderLeft: '6px solid #3b82f6' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={styles.kpiLabel}>TOTAL PACIENTES</span>
                        <span style={{ fontSize: '20px' }}>👥</span>
                    </div>
                    <div style={styles.kpiValue}>{metrics.total_pacientes}</div>
                    <div style={styles.kpiSub}>Expedientes activos</div>
                </div>
                <div style={{ ...styles.kpiCard, borderLeft: '6px solid #10b981' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={styles.kpiLabel}>CITAS HOY</span>
                        <span style={{ fontSize: '20px' }}>📅</span>
                    </div>
                    <div style={styles.kpiValue}>{metrics.citas_hoy}</div>
                    <div style={{ ...styles.kpiSub, cursor: 'pointer', color: '#10b981' }} onClick={() => navigate('/agenda')}>
                        Ver agenda ahora →
                    </div>
                </div>
                <div style={{ ...styles.kpiCard, borderLeft: '6px solid #f59e0b' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={styles.kpiLabel}>ESTADO DEL SISTEMA</span>
                        <span style={{ fontSize: '20px' }}>⚡</span>
                    </div>
                    <div style={styles.kpiValue}>ACTIVO</div>
                    <div style={{ ...styles.kpiSub, color: '#f59e0b' }}>Latencia: 45ms</div>
                </div>
            </div>

            {/* Quick Actions Header */}
            <div style={{ marginBottom: '20px', padding: '0 10px' }}>
                <h3 style={{ fontSize: '18px', fontWeight: '800', color: '#0f172a', margin: 0 }}>Accesos Directos</h3>
                <p style={{ fontSize: '13px', color: '#64748b', margin: '4px 0 0 0' }}>Módulos más utilizados en tu flujo de trabajo</p>
            </div>

            {/* Quick Actions Grid */}
            <div className="quick-actions-grid" style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                gap: '20px',
                marginBottom: '40px',
            }}>
                <div onClick={() => navigate('/gestion-citas')} style={quickActionStyle}>
                    <div style={iconCircleStyle('#eff6ff', '#2563eb')}>🗓️</div>
                    <span style={actionLabelStyle}>Nueva Cita</span>
                </div>
                <div onClick={() => navigate('/historia-clinica')} style={quickActionStyle}>
                    <div style={iconCircleStyle('#f0fdf4', '#16a34a')}>🏥</div>
                    <span style={actionLabelStyle}>Historias IA</span>
                </div>
                <div onClick={() => navigate('/finanzas')} style={quickActionStyle}>
                    <div style={iconCircleStyle('#fffbeb', '#d97706')}>💰</div>
                    <span style={actionLabelStyle}>Pagos</span>
                </div>
                <div onClick={() => navigate('/lista-espera')} style={quickActionStyle}>
                    <div style={iconCircleStyle('#faf5ff', '#9333ea')}>⏳</div>
                    <span style={actionLabelStyle}>Espera</span>
                </div>
                <div onClick={() => navigate('/escaner-qr')} style={quickActionStyle}>
                    <div style={iconCircleStyle('#fdf2f8', '#db2777')}>📷</div>
                    <span style={actionLabelStyle}>Escanear QR</span>
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
                                    <td colSpan="5" style={{padding: '40px', textAlign: 'center', color: '#64748b'}}>
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
    );
};

// Quick Action Card Style
const quickActionStyle = {
    backgroundColor: 'white',
    borderRadius: '24px',
    border: '1px solid #f1f5f9',
    padding: '24px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '12px',
    cursor: 'pointer',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)',
};

const iconCircleStyle = (bg, color) => ({
    width: '56px',
    height: '56px',
    borderRadius: '16px',
    backgroundColor: bg,
    color: color,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '24px',
    boxShadow: `0 8px 12px ${bg}80`
});

const actionLabelStyle = {
    fontWeight: '800',
    color: '#1e293b',
    fontSize: '13px',
    letterSpacing: '-0.2px'
};

export default Dashboard;