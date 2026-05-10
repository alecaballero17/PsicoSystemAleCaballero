import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/axiosConfig';
import authService from '../services/authService';

const Facturacion = () => {
    const navigate = useNavigate();
    const [transacciones, setTransacciones] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const fetchData = async () => {
        try {
            setLoading(true);
            const user = await authService.getCurrentUser(localStorage.getItem('token'));
            if (!user.clinica) {
                setError('No tienes una clínica asignada.');
                setLoading(false);
                return;
            }

            const response = await apiClient.get(`suscripciones/transacciones/`);
            setTransacciones(response.data);
        } catch (err) {
            console.error(err);
            setError('Error al obtener el historial de facturación.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    if (loading) return <div style={styles.loading}>Cargando historial...</div>;
    if (error) return <div style={styles.errorBox}>{error}</div>;

    return (
        <div style={styles.container}>
            <header style={styles.header}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '10px' }}>
                    <button onClick={() => navigate(-1)} style={styles.btnBack}>← Volver</button>
                    <h1 style={styles.headerTitle}>Historial de Facturación</h1>
                </div>
                <p style={styles.headerSubtitle}>Registro detallado de todos los movimientos financieros del Tenant.</p>
            </header>

            <div style={styles.card}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                    <h3 style={styles.sectionTitle}>Transacciones Recientes</h3>
                    <button onClick={fetchData} style={styles.btnRefresh}>🔄 Actualizar</button>
                </div>
                
                <div style={{ overflowX: 'auto' }}>
                    <table style={styles.table}>
                        <thead>
                            <tr style={styles.tableHead}>
                                <th style={styles.th}>FECHA</th>
                                <th style={styles.th}>DESCRIPCIÓN</th>
                                <th style={styles.th}>MÉTODO</th>
                                <th style={styles.th}>MONTO</th>
                                <th style={styles.th}>ESTADO</th>
                            </tr>
                        </thead>
                        <tbody>
                            {transacciones.length > 0 ? transacciones.map(t => (
                                <tr key={t.id} style={styles.tr}>
                                    <td style={styles.td}>{t.fecha_formateada}</td>
                                    <td style={styles.td}>
                                        <div style={{ fontWeight: '700', color: '#1e293b' }}>{t.descripcion}</div>
                                        <div style={{ fontSize: '10px', color: '#94a3b8' }}>ID: {t.id}</div>
                                    </td>
                                    <td style={styles.td}>
                                        <span style={styles.badgeMethod}>{t.metodo_pago}</span>
                                    </td>
                                    <td style={{ ...styles.td, fontWeight: '800', fontSize: '15px', color: t.tipo === 'CARGA' || t.descripcion.includes('Ingreso') ? '#16a34a' : '#dc2626' }}>
                                        {t.tipo === 'CARGA' || t.descripcion.includes('Ingreso') ? '+' : '-'}{t.monto} BOB
                                    </td>
                                    <td style={styles.td}>
                                        <span style={{ backgroundColor: '#dcfce7', color: '#166534', padding: '4px 10px', borderRadius: '12px', fontSize: '10px', fontWeight: 'bold' }}>COMPLETADO</span>
                                    </td>
                                </tr>
                            )) : (
                                <tr>
                                    <td colSpan="5" style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>
                                        No se encontraron movimientos financieros.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

const styles = {
    container: { padding: '32px', maxWidth: '1200px', margin: '0 auto', backgroundColor: '#f1f5f9', minHeight: '100vh' },
    header: { marginBottom: '32px' },
    headerTitle: { margin: 0, fontSize: '28px', color: '#0f172a', fontWeight: '800' },
    headerSubtitle: { margin: 0, color: '#64748b', fontSize: '16px' },
    btnBack: { backgroundColor: 'white', border: '1px solid #e2e8f0', padding: '8px 16px', borderRadius: '10px', cursor: 'pointer', color: '#475569', fontWeight: 'bold' },
    card: { backgroundColor: 'white', padding: '30px', borderRadius: '24px', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.05)', border: '1px solid #e2e8f0' },
    sectionTitle: { margin: 0, fontSize: '18px', color: '#1e293b', fontWeight: '800' },
    btnRefresh: { background: 'none', border: 'none', color: '#2563eb', cursor: 'pointer', fontWeight: 'bold', fontSize: '13px' },
    table: { width: '100%', borderCollapse: 'collapse' },
    tableHead: { borderBottom: '2px solid #f1f5f9' },
    th: { textAlign: 'left', padding: '15px 12px', fontSize: '11px', color: '#64748b', fontWeight: '900', textTransform: 'uppercase', letterSpacing: '0.5px' },
    tr: { borderBottom: '1px solid #f8fafc', transition: 'background 0.2s' },
    td: { padding: '15px 12px', fontSize: '13px', color: '#334155' },
    badgeMethod: { backgroundColor: '#f1f5f9', color: '#475569', padding: '4px 10px', borderRadius: '8px', fontSize: '10px', fontWeight: '800' },
    loading: { textAlign: 'center', padding: '100px', fontSize: '18px', color: '#64748b' },
    errorBox: { padding: '20px', backgroundColor: '#fef2f2', color: '#dc2626', border: '1px solid #fee2e2', borderRadius: '12px', margin: '32px' }
};

export default Facturacion;
