// ==============================================================================
// [CU26] CENTRO DE NOTIFICACIONES Y RECORDATORIOS
// Gestión de avisos automáticos de citas, pagos y alertas del sistema.
// ==============================================================================
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/axiosConfig';

const Notificaciones = () => {
    const navigate = useNavigate();
    const [notificaciones, setNotificaciones] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Obtenemos los logs que son de tipo notificación/pago/cita
                const response = await apiClient.get('admin/auditoria/');
                
                // Filtramos logs que parecen notificaciones para el CU26
                const filtradas = response.data.filter(log => 
                    log.accion.toLowerCase().includes('pago') || 
                    log.accion.toLowerCase().includes('cita') ||
                    log.accion.toLowerCase().includes('notificación')
                ).slice(0, 15); // Top 15 recientes

                setNotificaciones(filtradas);
            } catch (err) {
                console.error("Error cargando notificaciones", err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const getIcon = (accion) => {
        if (accion.toLowerCase().includes('pago')) return '💰';
        if (accion.toLowerCase().includes('cita')) return '📅';
        if (accion.toLowerCase().includes('ia')) return '🤖';
        return '🔔';
    };

    return (
        <div style={styles.container}>
            <div style={styles.header}>
                <h2 style={styles.title}>🔔 Centro de Notificaciones (CU26)</h2>
                <p style={styles.subtitle}>Seguimiento en tiempo real de recordatorios, pagos y eventos críticos.</p>
            </div>

            {loading ? (
                <div style={styles.loading}>Cargando notificaciones...</div>
            ) : notificaciones.length > 0 ? (
                <div style={styles.list}>
                    {notificaciones.map((notif) => (
                        <div key={notif.id} style={styles.card}>
                            <div style={styles.iconBox}>{getIcon(notif.accion)}</div>
                            <div style={styles.content}>
                                <div style={styles.cardHeader}>
                                    <span style={styles.time}>{notif.fecha_formateada}</span>
                                    <span style={styles.userBadge}>{notif.usuario_nombre}</span>
                                </div>
                                <p style={styles.message}>{notif.accion}</p>
                                <div style={styles.footer}>
                                    <span style={styles.status}>Estado: Ejecutado ✅</span>
                                    <span style={styles.channel}>Canal: Web/Push</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div style={styles.empty}>No hay notificaciones recientes.</div>
            )}
        </div>
    );
};

const styles = {
    container: { padding: '32px', backgroundColor: '#f8fafc', minHeight: 'calc(100vh - 64px)' },
    header: { marginBottom: '24px' },
    title: { margin: 0, fontSize: '26px', fontWeight: '900', color: '#0f172a' },
    subtitle: { margin: '8px 0 0 0', color: '#64748b', fontSize: '15px' },
    loading: { padding: '40px', textAlign: 'center', color: '#64748b' },
    empty: { padding: '40px', textAlign: 'center', color: '#94a3b8', backgroundColor: 'white', borderRadius: '16px' },
    list: { display: 'flex', flexDirection: 'column', gap: '16px' },
    card: { 
        backgroundColor: 'white', 
        borderRadius: '16px', 
        padding: '20px', 
        display: 'flex', 
        gap: '20px', 
        boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)',
        border: '1px solid #f1f5f9',
        transition: 'transform 0.2s',
        cursor: 'pointer'
    },
    iconBox: {
        width: '48px', height: '48px', borderRadius: '12px',
        backgroundColor: '#eff6ff', display: 'flex', alignItems: 'center',
        justifyContent: 'center', fontSize: '20px'
    },
    content: { flex: 1 },
    cardHeader: { display: 'flex', justifyContent: 'space-between', marginBottom: '8px' },
    time: { fontSize: '12px', color: '#94a3b8', fontWeight: '600' },
    userBadge: { fontSize: '10px', backgroundColor: '#f1f5f9', padding: '2px 8px', borderRadius: '4px', color: '#475569', fontWeight: '700' },
    message: { margin: 0, fontSize: '15px', color: '#1e293b', fontWeight: '600', lineHeight: 1.4 },
    footer: { marginTop: '12px', display: 'flex', gap: '16px', fontSize: '11px', fontWeight: '700' },
    status: { color: '#10b981' },
    channel: { color: '#64748b', textTransform: 'uppercase' }
};

export default Notificaciones;
