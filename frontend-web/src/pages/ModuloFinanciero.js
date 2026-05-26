import React, { useState, useEffect } from 'react';
import apiClient from '../api/axiosConfig';

const ModuloFinanciero = () => {
    const [transacciones, setTransacciones] = useState([]);
    const [pacientes, setPacientes] = useState([]);
    const [loading, setLoading] = useState(true);

    // Estados para el Modal de Registro
    const [showModal, setShowModal] = useState(false);
    const [pacienteId, setPacienteId] = useState('');
    const [monto, setMonto] = useState('');
    const [concepto, setConcepto] = useState('');
    const [metodoPago, setMetodoPago] = useState('EFECTIVO');
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        fetchTransacciones();
        fetchPacientes();
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

    const fetchPacientes = async () => {
        try {
            const response = await apiClient.get('pacientes/');
            setPacientes(response.data);
        } catch (err) {
            console.error("Error al cargar pacientes", err);
        }
    };

    const totalRecaudado = transacciones.reduce((acc, t) => acc + parseFloat(t.monto), 0);

    const handleDownloadPDF = async (transaccionId) => {
        try {
            const response = await apiClient.get(`finanzas/transacciones/${transaccionId}/pdf/`, {
                responseType: 'blob'
            });
            const blob = new Blob([response.data], { type: 'application/pdf' });
            const url = window.URL.createObjectURL(blob);
            window.open(url, '_blank');
        } catch (err) {
            console.error("Error al descargar el recibo", err);
            alert("Error al descargar el recibo.");
        }
    };

    const handleRegisterPayment = async (e) => {
        e.preventDefault();
        if (!pacienteId || !monto || !concepto) {
            alert("Por favor rellene todos los campos obligatorios.");
            return;
        }
        setSubmitting(true);
        try {
            const response = await apiClient.post('finanzas/transacciones/', {
                paciente: parseInt(pacienteId),
                monto: parseFloat(monto),
                concepto: concepto,
                metodo_pago: metodoPago
            });
            if (response.status === 201) {
                alert(`✅ Pago registrado con éxito. Comprobante: ${response.data.nro_comprobante}`);
                // Limpiar campos
                setPacienteId('');
                setMonto('');
                setConcepto('');
                setMetodoPago('EFECTIVO');
                setShowModal(false);
                // Actualizar lista
                fetchTransacciones();
            }
        } catch (err) {
            console.error("Error al registrar pago", err);
            alert("❌ No se pudo registrar el pago. Verifique los datos.");
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div style={styles.container}>
            <header style={styles.header}>
                <h2 style={styles.title}>CONTROL DE PAGOS Y RECIBOS (CU11/12)</h2>
                <button 
                    style={styles.btnPrimary}
                    onClick={() => setShowModal(true)}
                >
                    + REGISTRAR PAGO
                </button>
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

            {/* Modal para registrar un nuevo pago */}
            {showModal && (
                <div style={styles.modalOverlay}>
                    <div style={styles.modalContent}>
                        <h3 style={styles.modalTitle}>💵 REGISTRAR NUEVO PAGO</h3>
                        <form onSubmit={handleRegisterPayment}>
                            <div style={styles.formGroup}>
                                <label style={styles.label}>PACIENTE *</label>
                                <select 
                                    value={pacienteId}
                                    onChange={e => setPacienteId(e.target.value)}
                                    style={styles.select}
                                    required
                                >
                                    <option value="">-- Seleccionar Paciente --</option>
                                    {pacientes.map(p => (
                                        <option key={p.id} value={p.id}>
                                            {p.nombre} (CI: {p.ci})
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div style={styles.formGroup}>
                                <label style={styles.label}>MONTO (BS) *</label>
                                <input 
                                    type="number" 
                                    step="0.01"
                                    min="0.01"
                                    value={monto}
                                    onChange={e => setMonto(e.target.value)}
                                    style={styles.input}
                                    placeholder="Ej. 150.00"
                                    required
                                />
                            </div>

                            <div style={styles.formGroup}>
                                <label style={styles.label}>CONCEPTO *</label>
                                <input 
                                    type="text" 
                                    value={concepto}
                                    onChange={e => setConcepto(e.target.value)}
                                    style={styles.input}
                                    placeholder="Ej. Terapia inicial, Sesión de control"
                                    required
                                />
                            </div>

                            <div style={styles.formGroup}>
                                <label style={styles.label}>MÉTODO DE PAGO *</label>
                                <select 
                                    value={metodoPago}
                                    onChange={e => setMetodoPago(e.target.value)}
                                    style={styles.select}
                                    required
                                >
                                    <option value="EFECTIVO">Efectivo</option>
                                    <option value="TRANSFERENCIA">Transferencia Bancaria</option>
                                    <option value="QR">QR / Pago Móvil</option>
                                </select>
                            </div>

                            <div style={styles.btnGroup}>
                                <button 
                                    type="button" 
                                    onClick={() => setShowModal(false)}
                                    style={styles.btnCancel}
                                >
                                    Cancelar
                                </button>
                                <button 
                                    type="submit"
                                    disabled={submitting}
                                    style={styles.btnSave}
                                >
                                    {submitting ? 'Guardando...' : 'Guardar Pago'}
                                </button>
                            </div>
                        </form>
                    </div>
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
    summaryValue: { fontSize: '24px', color: '#0891b2', fontWeight: 'bold' },
    
    // Estilos del Modal
    modalOverlay: {
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        backgroundColor: 'rgba(15, 23, 42, 0.6)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 1000
    },
    modalContent: {
        backgroundColor: 'white',
        padding: '30px',
        borderRadius: '12px',
        width: '450px',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        animation: 'fadeIn 0.2s ease-out'
    },
    modalTitle: { margin: '0 0 20px 0', fontSize: '18px', fontWeight: 'bold', color: '#0f172a', borderBottom: '1px solid #e2e8f0', paddingBottom: '10px' },
    formGroup: { marginBottom: '15px' },
    label: { display: 'block', fontSize: '11px', fontWeight: 'bold', color: '#475569', marginBottom: '5px' },
    input: { width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '14px', outline: 'none' },
    select: { width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '14px', outline: 'none', backgroundColor: 'white' },
    btnGroup: { display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '25px' },
    btnCancel: { padding: '10px 20px', backgroundColor: '#f1f5f9', color: '#475569', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' },
    btnSave: { padding: '10px 20px', backgroundColor: '#0891b2', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }
};

export default ModuloFinanciero;
