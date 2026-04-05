import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import dashboardService from '../services/dashboardService'; // <-- 1. IMPORTAMOS TU SERVICIO
import axios from 'axios';
import { dashboardStyles as styles } from '../styles/dashboardStyles';

const Dashboard = () => {
    const navigate = useNavigate();
    
    // ESTADOS
    const [pacientes, setPacientes] = useState([]);
    const [metrics, setMetrics] = useState({ total_pacientes: 0, citas_hoy: 0 });
    const [cargando, setCargando] = useState(true);
    
    // DATOS DE SESIÓN
    const userName = localStorage.getItem('userName') || 'USUARIO';
    const userRole = localStorage.getItem('userRole') || 'ADMIN';

    // FUNCIÓN DE CARGA DE DATOS (CONEXIÓN CON DJANGO)
    const fetchData = useCallback(async () => {
        const token = localStorage.getItem('userToken');
        
        // Si no hay token, redirigir al login por seguridad
        if (!token) {
            navigate('/');
            return;
        }

        try {
            // RNF-01: Peticiones paralelas para optimizar tiempos de respuesta
            const [resPacientes, metricasData] = await Promise.all([
                axios.get('http://127.0.0.1:8000/api/pacientes/', {
                    headers: { 'Authorization': `Bearer ${token}` }
                }),
                dashboardService.getMetrics() 
            ]);
            
            setPacientes(Array.isArray(resPacientes.data) ? resPacientes.data : []);
            setMetrics(metricasData.metricas || metricasData); 
            setCargando(false);

        } catch (error) {
            console.error("Error cargando datos de Django:", error.response?.data || error.message);
            setCargando(false);
            
            // --- NUEVO: MANEJO DE ERROR 403 (RF-29 Multi-tenant / Usuarios sin clínica) ---
            if (error.response?.status === 403) {
                // El backend (Django) envía el texto "Su usuario no tiene una clínica asignada..." en error.response.data.detail
                const mensajeError = error.response.data.detail || "Error de permisos. Contacte al administrador.";
                alert(`⚠️ ALERTA DE SEGURIDAD\n\n${mensajeError}`);
                // Opcional: Podrías redirigirlo al login o a una página de "Configuración Pendiente"
            }
            
            // Si el token expiró (401), mandamos al login
            if (error.response?.status === 401) {
                localStorage.clear();
                navigate('/');
            }
        }
    }, [navigate]);

    // DISPARADOR INICIAL
    useEffect(() => {
        fetchData();
    }, [fetchData]);

    return (
        <div style={styles.layout}>
            {/* SIDEBAR: Navegación Lateral */}
            <aside style={styles.sidebar}>
                <div style={styles.brandContainer}>
                    <div style={styles.brandLogo}></div>
                    <span style={styles.brandText}>
                        PSICOSYSTEM <span style={styles.brandVersion}>v1.0.4</span>
                    </span>
                </div>
                
                <nav style={styles.navSection}>
                    <p style={styles.sectionLabel}>PRINCIPAL</p>
                    <div style={styles.navItemActive}>Vista General Analítica</div>
                    <div 
                        style={styles.navItem} 
                        onClick={() => navigate('/registro-paciente')}
                    >
                        Gestión de Expedientes
                    </div>
                </nav>

                {userRole === 'ADMIN' && (
                    <nav style={styles.navSection}>
                        <p style={styles.sectionLabel}>ADMINISTRACIÓN</p>
                        <div style={styles.navItem}>Recursos Humanos (RF-28)</div>
                        <div 
                            style={styles.navItem} 
                            onClick={() => navigate('/registro-clinica')}
                        >
                            Configuración de Clínica
                        </div>
                    </nav>
                )}

                <div style={styles.sidebarFooter}>
                    <div style={styles.sessionInfo}>
                        <div style={styles.statusDot}></div>
                        <span>Servidor: Online</span>
                    </div>
                    <button 
                        onClick={async () => { await authService.logout(); navigate('/'); }} 
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
                    <div style={styles.headerUser}>
                        <span style={styles.userRoleTag}>{userRole}</span>
                        <span style={styles.userName}>{userName}</span>
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
                            <h3 style={styles.panelTitle}>EXPEDIENTES RECIENTES (TRAZABILIDAD T014)</h3>
                            <button 
                                onClick={() => navigate('/registro-paciente')} 
                                style={styles.mainActionBtn}
                            >
                                + NUEVO REGISTRO
                            </button>
                        </div>
                        
                        <div style={styles.tableContainer}>
                            <table style={styles.table}>
                                <thead>
                                    <tr style={styles.tableHeader}>
                                        <th style={styles.th}>ID</th>
                                        <th style={styles.th}>PACIENTE</th>
                                        <th style={styles.th}>IDENTIFICACIÓN</th>
                                        <th style={styles.th}>ESTADO</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {pacientes.length > 0 ? (
                                        pacientes.map((p) => (
                                            <tr key={p.id} style={styles.tableRow}>
                                                <td style={styles.td}>#{p.id}</td>
                                                <td style={styles.tdBold}>
                                                    {/* 4. BUG ARREGLADO: Solo leemos nombre_completo o nombre */}
                                                    {`${p.nombre_completo || p.nombre || ''}`.toUpperCase()}
                                                </td>
                                                <td style={styles.td}>{p.ci || p.identificacion || 'S/N'}</td>
                                                <td style={styles.td}>
                                                    <span style={styles.statusActive}>ACTIVO</span>
                                                </td>
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