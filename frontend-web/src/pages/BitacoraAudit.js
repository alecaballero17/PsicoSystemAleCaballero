import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/axiosConfig';

const BitacoraAudit = () => {
    const navigate = useNavigate();
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const response = await apiClient.get('admin/auditoria/');
                setLogs(response.data);
            } catch (err) {
                console.error("Error cargando bitácora", err);
                setError("No se pudieron cargar los registros de auditoría.");
            } finally {
                setLoading(false);
            }
        };
        fetchLogs();
    }, []);

    return (
        <div style={styles.layout}>
            <div style={styles.container}>
                <header style={styles.header}>
                    <button onClick={() => navigate('/dashboard')} style={styles.btnBack}>← VOLVER</button>
                    <h2 style={styles.title}>BITÁCORA DE AUDITORÍA</h2>
                    <p style={styles.subtitle}>Registro de accesos y movimientos críticos en el sistema</p>
                </header>

                {error && <div style={styles.errorBox}>{error}</div>}

                <div style={styles.tableCard}>
                    <table style={styles.table}>
                        <thead>
                            <tr style={styles.tableHead}>
                                <th style={styles.th}>FECHA Y HORA</th>
                                <th style={styles.th}>USUARIO</th>
                                <th style={styles.th}>ACCIÓN REALIZADA</th>
                                <th style={styles.th}>DIRECCIÓN IP</th>
                                <th style={styles.th}>DISPOSITIVO</th>
                            </tr>
                        </thead>
                        <tbody>
                            {logs.length > 0 ? logs.map(log => (
                                <tr key={log.id} style={styles.tr}>
                                    <td style={styles.td}>{log.fecha_formateada}</td>
                                    <td style={styles.td}>
                                        <span style={styles.badgeUser}>{log.usuario_nombre}</span>
                                    </td>
                                    <td style={styles.td}>{log.accion}</td>
                                    <td style={styles.td}>{log.ip_address || '---'}</td>
                                    <td style={{...styles.td, fontSize: '10px', color: '#64748b'}} title={log.user_agent}>
                                        {log.user_agent ? (log.user_agent.length > 30 ? log.user_agent.substring(0, 30) + '...' : log.user_agent) : 'N/A'}
                                    </td>
                                </tr>
                            )) : !loading && (
                                <tr>
                                    <td colSpan="5" style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>
                                        No hay registros de auditoría disponibles.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                    {loading && <div style={{ padding: '40px', textAlign: 'center' }}>Cargando bitácora...</div>}
                </div>
            </div>
        </div>
    );
};

const styles = {
    layout: { padding: '32px', backgroundColor: '#f1f5f9', minHeight: 'calc(100vh - 64px)' },
    container: { maxWidth: '1200px', margin: '0 auto' },
    header: { marginBottom: '24px' },
    btnBack: { backgroundColor: 'white', border: '1px solid #e2e8f0', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', fontSize: '12px', color: '#64748b', marginBottom: '16px' },
    title: { margin: 0, fontSize: '24px', color: '#0f172a', fontWeight: '800' },
    subtitle: { margin: '5px 0 0 0', color: '#64748b', fontSize: '14px' },
    tableCard: { backgroundColor: 'white', borderRadius: '16px', boxShadow: '0 4px 15px rgba(0,0,0,0.05)', overflow: 'hidden' },
    table: { width: '100%', borderCollapse: 'collapse' },
    tableHead: { backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0' },
    th: { textAlign: 'left', padding: '16px', fontSize: '12px', fontWeight: 'bold', color: '#64748b', textTransform: 'uppercase' },
    tr: { borderBottom: '1px solid #f1f5f9' },
    td: { padding: '16px', fontSize: '13px', color: '#334155' },
    badgeUser: { backgroundColor: '#eff6ff', color: '#2563eb', padding: '4px 10px', borderRadius: '6px', fontWeight: 'bold', fontSize: '11px' },
    errorBox: { padding: '16px', backgroundColor: '#fef2f2', color: '#dc2626', borderRadius: '8px', marginBottom: '20px', fontSize: '13px', border: '1px solid #fee2e2' }
};

export default BitacoraAudit;
