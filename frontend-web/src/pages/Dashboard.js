import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import dashboardService from '../services/dashboardService';
import pacienteService from '../services/pacienteService'; 
import { dashboardStyles as styles } from '../styles/dashboardStyles';
import { useAuth } from '../context/AuthContext'; 

const Dashboard = () => {
    const navigate = useNavigate();
    const { user, tenant, logout } = useAuth(); 
    
    // [ALINEACIÓN RF-29] - Visualización dinámica de identidad del Tenant: El sistema refleja los metadatos institucionales actualizados mediante T024.    
    // ESTADOS DE UI
    const [pacientes, setPacientes] = useState([]);
    const [citasHoy, setCitasHoy] = useState([]);
    const [metrics, setMetrics] = useState({ total_pacientes: 0, citas_hoy: 0 });
    const [cargando, setCargando] = useState(true);
    
    // OBTENEMOS DATOS DE SESIÓN
    const userName = user?.name || 'USUARIO';
    const userRole = user?.role || 'ADMIN';
    const token = user?.token;
    const apiClient = authService.apiClient;

    // FUNCIÓN DE CARGA DE DATOS (CONEXIÓN CENTRALIZADA)
    const fetchData = useCallback(async () => {
        if (!token) {
            navigate('/');
            return;
        }

        try {
            setCargando(true);
            
            // RNF-01: Peticiones paralelas usando los servicios centralizados
            const [listaPacientes, metricasData, listaCitas] = await Promise.all([
                pacienteService.getPacientes(), 
                dashboardService.getMetrics(),
                apiClient.get('logistica/gestion/')
            ]);
            
            setPacientes(Array.isArray(listaPacientes) ? listaPacientes : []);
            
            // Filtrar citas de hoy
            const hoyStr = new Date().toISOString().split('T')[0];
            const citasDeHoy = (Array.isArray(listaCitas.data) ? listaCitas.data : []).filter(c => 
                c.fecha_hora.startsWith(hoyStr) && c.estado !== 'CANCELADA'
            );
            setCitasHoy(citasDeHoy);
            
            // --- APLICAMOS EL MAPEO DE DATOS AQUÍ ---
            const datosCrudos = metricasData.metricas || metricasData;
            setMetrics({
                total_pacientes: datosCrudos.total_pacientes || 0,
                citas_hoy: datosCrudos.citas_pendientes || 0  // Transformamos 'pendientes' a 'hoy'
            });
            // ----------------------------------------

            setCargando(false);

        } catch (error) {
            console.error("Error cargando datos de Django:", error.response?.data || error.message);
            setCargando(false);
            
            // --- MANEJO DE ERROR 403 (RF-29 Multi-tenant) ---
            if (error.response?.status === 403) {
                const mensajeError = error.response.data.detail || "Error de permisos. Contacte al administrador.";
                alert(`⚠️ ALERTA DE SEGURIDAD\n\n${mensajeError}`);
            }
            
            // Si el token expiró (401), limpiamos la RAM. 
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
                fetchData(); // Recargamos lista y métricas
            } catch (error) {
                console.error("Error al dar de baja:", error);
                alert("No se pudo completar la acción. Verifique sus permisos de administrador.");
            }
        }
    };

    // DISPARADOR INICIAL
    useEffect(() => {
        fetchData();
    }, [fetchData]);

    return (
        <div style={styles.layout}>
            {/* SIDEBAR: Navegación Lateral */}
            <aside style={styles.sidebar}>
                {/* [ALINEACIÓN RF-29] - Identidad visual dinámica del Tenant: El sistema personaliza la interfaz según la pertenencia organizacional del usuario autenticado. */}
                <div style={styles.brandContainer}>
                    {tenant.logo ? (
                        <img src={tenant.logo} alt="Tenant Logo" style={{ width: '40px', height: '40px', borderRadius: '8px', objectFit: 'cover' }} />
                    ) : (
                        <div style={styles.brandLogo}>
                            <span style={{ fontSize: '20px' }}>🏥</span>
                        </div>
                    )}
                    <span style={styles.brandText}>
                        {tenant.nombre?.toUpperCase() || 'PSICOSYSTEM'} <span style={styles.brandVersion}>v1.0.4</span>
                    </span>
                </div>
                
                <nav style={styles.navSection}>
                    <p style={styles.sectionLabel}>PRINCIPAL</p>
                    <div style={styles.navItemActive}>Vista General Analítica</div>
                    {/* [SPRINT 2] Gestión de Pacientes (CU13) */}
                    <div style={styles.navItem} onClick={() => navigate('/pacientes')}>
                        Gestión de Pacientes
                    </div>

                    {/* [SPRINT 2] Agenda de Citas (CU14/15) */}
                    <div style={styles.navItem} onClick={() => navigate('/citas')}>
                        Agenda de Citas
                    </div>

                    {/* [SPRINT 2] IA Predictiva */}
                    <div style={styles.navItem} onClick={() => navigate('/ia')}>
                        Asistente IA (Gemini)
                    </div>

                    {/* [SPRINT 2] Pagos y Recibos (CU11/12) */}
                    <div style={styles.navItem} onClick={() => navigate('/pagos')}>
                        Módulo Financiero
                    </div>

                    {/* [VIP] Reportes por Voz para el Jefe */}
                    <div style={{ ...styles.navItem, color: '#f59e0b', fontWeight: 'bold' }} onClick={() => navigate('/reporte-voz')}>
                        🎙️ Reportes por Voz
                    </div>
                </nav>

                {userRole === 'ADMIN' && (
                    <nav style={styles.navSection}>
                        <p style={styles.sectionLabel}>ADMINISTRACIÓN</p>
                        {/* [SPRINT 1 - CU-05] Gestión de Personal Clínico completa (especialidades, horarios) -> Sprint 1 Finalizado */}
                        {userRole === 'ADMIN' && (
                            <div style={styles.navItem} onClick={() => navigate('/gestion-personal')}>
                                Gestión de Personal Clínico (RF-28)
                            </div>
                        )}

                        {userRole === 'ADMIN' && (
                            <div 
                                style={styles.navItem} 
                                onClick={() => navigate('/configuracion-clinica')}
                            >
                                Configuración de Clínica
                            </div>
                        )}

                        {userRole === 'ADMIN' && (
                            <div 
                                style={{ ...styles.navItem, borderLeft: '3px solid #1e40af', backgroundColor: 'rgba(30, 64, 175, 0.05)' }} 
                                onClick={() => navigate('/admin-reportes')}
                            >
                                📊 Reportes y Auditoría
                            </div>
                        )}

                        {/* [SPRINT 1 - T025] Interfaz de monitoreo de límites SaaS. */}
                        {userRole === 'ADMIN' && (
                            <div 
                                style={styles.navItem} 
                                onClick={() => navigate('/suscripcion')}
                            >
                                Suscripción SaaS (CU-24)
                            </div>
                        )}
                    </nav>
                )}

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

            {/* MAIN CONTENT: Área de Trabajo */}
            <main style={styles.main}>
                <header style={styles.header}>
                    <div style={styles.headerPath}>Consola / Dashboard</div>
                    <div style={{ ...styles.headerUser, display: 'flex', flexDirection: 'column', alignItems: 'flex-end', justifyContent: 'center' }}>
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
                    {/* INDICADORES KPI */}
                    <div style={styles.kpiGrid}>
                        <div style={styles.kpiCard}>
                            <span style={styles.kpiLabel}>TOTAL PACIENTES</span>
                            <div style={styles.kpiValue}>{metrics.total_pacientes}</div>
                            <div style={styles.kpiSub}>Sincronizado con PostgreSQL</div>
                        </div>
                        <div style={styles.kpiCard}>
                            <span style={styles.kpiLabel}>CITAS HOY</span>
                            <div style={styles.kpiValue}>{metrics.citas_hoy}</div>
                            <div style={styles.kpiSub}>Módulo Agenda (Sprint 2)</div>
                        </div>
                        <div style={styles.kpiCard}>
                            <span style={styles.kpiLabel}>ESTADO API</span>
                            <div style={styles.kpiValue}>ONLINE</div>
                            <div style={styles.kpiSub}>Latencia: 24ms</div>
                        </div>
                    </div>

                    {/* PANEL DE TABLA */}
                    <div style={styles.panelSection}>
                        <div style={styles.panelHeader}>
                            <h3 style={styles.panelTitle}>PANEL DE TRABAJO DIARIO - CITAS HOY</h3>
                            <button 
                                onClick={() => navigate('/citas')} 
                                style={styles.mainActionBtn}
                            >
                                IR A AGENDA
                            </button>
                        </div>
                        
                        <div style={styles.tableContainer}>
                            <table style={styles.table}>
                                <thead>
                                    <tr style={styles.tableHeader}>
                                        <th style={styles.th}>HORA</th>
                                        <th style={styles.th}>PACIENTE</th>
                                        <th style={styles.th}>MOTIVO</th>
                                        <th style={styles.th}>ESTADO</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {citasHoy.length > 0 ? (
                                        citasHoy.map((c) => (
                                            <tr key={c.id} style={styles.tableRow}>
                                                <td style={styles.tdBold}>{new Date(c.fecha_hora).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</td>
                                                <td style={styles.td}>{c.paciente_nombre}</td>
                                                <td style={styles.td}>{c.motivo || 'Sesión General'}</td>
                                                <td style={styles.td}>
                                                    <span style={styles.statusActive}>{c.estado}</span>
                                                </td>
                                            </tr>
                                        ))
                                    ) : (
                                        <tr>
                                            <td colSpan="4" style={{padding: '40px', textAlign: 'center', color: '#64748b'}}>
                                                No tienes citas programadas para hoy.
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* PANEL DE PACIENTES RECIENTES */}
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

export default Dashboard;