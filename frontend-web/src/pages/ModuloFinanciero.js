import React, { useState, useEffect } from 'react';
import apiClient from '../api/axiosConfig';

const ModuloFinanciero = () => {
    const [transacciones, setTransacciones] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchTransacciones();
    }, []);

    const fetchTransacciones = async () => {
        try {
            const response = await apiClient.get('finanzas/transacciones/');
            setTransacciones(response.data);
        } catch (err) {
            console.error("Error al cargar finanzas", err);
        } finally {
            setLoading(false);
        }
    };

    const totalRecaudado = transacciones.reduce((acc, t) => acc + parseFloat(t.monto), 0);

    const handleDownloadPDF = async (transaccionId) => {
        try {
            // Usamos window.open para descargar el archivo directamente
            const token = localStorage.getItem('userToken');
            const url = `${apiClient.defaults.baseURL}finanzas/transacciones/${transaccionId}/pdf/?token=${token}`;
            
            window.open(url, '_blank');
        } catch (err) {
            alert("Error al descargar el recibo.");
        }
    };

    return (
        <div style={styles.container}>
            <header style={styles.header}>
                <h2 style={styles.title}>CONTROL DE PAGOS Y RECIBOS (CU11/12)</h2>
                <button style={styles.btnPrimary}>+ REGISTRAR PAGO</button>
            </header>

            <div style={styles.summaryCard}>
                <div style={styles.summaryItem}>
                    <span style={styles.summaryLabel}>TOTAL RECAUDADO</span>
                    <span style={styles.summaryValue}>{totalRecaudado.toFixed(2)} BS</span>
                </div>
                <div style={styles.summaryItem}>
                    <span style={styles.summaryLabel}>TRANSACCIONES</span>
                    <span style={styles.summaryValue}>{transacciones.length}</span>
                </div>
            </div>

            {loading ? (
                <p>Cargando transacciones...</p>
            ) : (
                <div style={styles.tableCard}>
                    <table style={styles.table}>
                        <thead>
                            <tr style={styles.trHead}>
                                <th style={styles.th}>FECHA</th>
                                <th style={styles.th}>PACIENTE</th>
                                <th style={styles.th}>CONCEPTO</th>
                                <th style={styles.th}>MONTO</th>
                                <th style={styles.th}>MÉTODO</th>
                                <th style={styles.th}>ACCIONES</th>
                            </tr>
                        </thead>
                        <tbody>
                            {transacciones.map(t => (
                                <tr key={t.id} style={styles.trBody}>
                                    <td style={styles.td}>{new Date(t.fecha).toLocaleDateString()}</td>
                                    <td style={styles.td}>{t.paciente_nombre}</td>
                                    <td style={styles.td}>{t.concepto}</td>
                                    <td style={styles.td}><strong>{t.monto} BS</strong></td>
                                    <td style={styles.td}>{t.metodo_pago}</td>
                                    <td style={styles.td}>
                                        <button 
                                            style={styles.btnReceipt}
                                            onClick={() => handleDownloadPDF(t.id)}
                                        >
                                            📄 VER RECIBO
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            {transacciones.length === 0 && (
                                <tr>
                                    <td colSpan="6" style={{padding: '20px', textAlign: 'center'}}>No hay transacciones registradas.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

const styles = {
    container: { padding: '40px', backgroundColor: '#f8fafc', minHeight: '100vh' },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' },
    title: { margin: 0, color: '#0f172a', fontSize: '24px', fontWeight: 'bold' },
    btnPrimary: { padding: '12px 24px', backgroundColor: '#0891b2', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' },
    tableCard: { backgroundColor: 'white', borderRadius: '12px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)', overflow: 'hidden' },
    table: { width: '100%', borderCollapse: 'collapse' },
    trHead: { backgroundColor: '#f1f5f9', textAlign: 'left' },
    th: { padding: '15px', fontSize: '12px', fontWeight: 'bold', color: '#64748b' },
    trBody: { borderTop: '1px solid #f1f5f9' },
    td: { padding: '15px', fontSize: '14px', color: '#334155' },
    btnReceipt: { padding: '6px 12px', backgroundColor: '#f1f5f9', color: '#475569', border: '1px solid #cbd5e1', borderRadius: '4px', cursor: 'pointer', fontSize: '11px', fontWeight: 'bold' },
    summaryCard: { display: 'flex', gap: '20px', marginBottom: '30px' },
    summaryItem: { backgroundColor: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)', flex: 1, display: 'flex', flexDirection: 'column' },
    summaryLabel: { fontSize: '12px', color: '#64748b', fontWeight: 'bold', marginBottom: '5px' },
    summaryValue: { fontSize: '24px', color: '#0891b2', fontWeight: 'bold' }
};

export default ModuloFinanciero;
