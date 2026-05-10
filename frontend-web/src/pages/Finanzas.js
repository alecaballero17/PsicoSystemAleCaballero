// ==============================================================================
// [SPRINT 2 - RF-25/RF-26 / T058/T059 / CU26] Módulo Financiero
// Saldos, registro de pagos, historial de transacciones y comprobante PDF.
// ==============================================================================
import React, { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import finanzaService from '../services/finanzaService';
import pacienteService from '../services/pacienteService';
import { useToast } from '../components/Toast';

const TIPO_COLORS = {
    PAGO: { bg: '#dcfce7', color: '#15803d', icon: '💰' },
    DEUDA: { bg: '#fee2e2', color: '#dc2626', icon: '📋' },
    AJUSTE: { bg: '#fef3c7', color: '#d97706', icon: '⚙️' },
};

const Finanzas = () => {
    const { user } = useAuth();
    const { showToast, ToastContainer } = useToast();

    const [pacientes, setPacientes] = useState([]);
    const [transacciones, setTransacciones] = useState([]);
    const [selectedPaciente, setSelectedPaciente] = useState('');
    const [saldoInfo, setSaldoInfo] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showPagoForm, setShowPagoForm] = useState(false);
    const [isProcessingPayment, setIsProcessingPayment] = useState(false);
    const [paymentSuccess, setPaymentSuccess] = useState(false);

    // Form de pago
    const [pagoForm, setPagoForm] = useState({
        paciente: '',
        monto: '',
        tipo: 'PAGO',
        descripcion: '',
    });

    const fetchData = useCallback(async () => {
        try {
            setLoading(true);
            const [pacData, txData] = await Promise.all([
                pacienteService.getPacientes(),
                finanzaService.getTransacciones(),
            ]);
            setPacientes(Array.isArray(pacData) ? pacData : []);
            setTransacciones(Array.isArray(txData) ? txData : []);
        } catch {
            showToast('Error cargando datos financieros', 'error');
        } finally {
            setLoading(false);
        }
    }, [showToast]);

    useEffect(() => { fetchData(); }, [fetchData]);

    const handleConsultarSaldo = async (pacienteId) => {
        if (!pacienteId) return;
        try {
            const data = await finanzaService.getSaldo(pacienteId);
            setSaldoInfo(data);
            setSelectedPaciente(pacienteId);
        } catch {
            showToast('Error al consultar saldo', 'error');
        }
    };

    const handleRegistrarPago = async (e) => {
        e.preventDefault();
        
        // --- SIMULADOR DE PASARELA DE PAGOS (RF-25) ---
        // Para demostrar la UX de procesamiento de un pago online.
        setIsProcessingPayment(true);
        setPaymentSuccess(false);

        // Simulamos 2 segundos conectando a la pasarela
        setTimeout(() => {
            setIsProcessingPayment(false);
            setPaymentSuccess(true);
            
            // 1 segundo de check verde antes de registrar en BD
            setTimeout(async () => {
                try {
                    await finanzaService.registrarTransaccion(pagoForm);
                    showToast('Transacción registrada exitosamente', 'success');
                    setPagoForm({ paciente: '', monto: '', tipo: 'PAGO', descripcion: '' });
                    setShowPagoForm(false);
                    setPaymentSuccess(false);
                    fetchData();
                    if (selectedPaciente) handleConsultarSaldo(selectedPaciente);
                } catch (err) {
                    const msg = err.response?.data?.detail || 'Error al registrar la transacción';
                    showToast(msg, 'error');
                    setPaymentSuccess(false);
                }
            }, 1000);
        }, 2000);
    };

    const handleDescargarPDF = async (txId) => {
        try {
            await finanzaService.descargarComprobante(txId);
            showToast('Comprobante abierto en nueva pestaña', 'info');
        } catch {
            showToast('Error al generar el comprobante PDF', 'error');
        }
    };

    const formatMonto = (monto) => {
        return parseFloat(monto).toLocaleString('es-BO', { minimumFractionDigits: 2 });
    };

    const formatFecha = (iso) => new Date(iso).toLocaleDateString('es-BO', {
        day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
    });

    // Métricas
    const totalIngresos = transacciones.filter(t => t.tipo === 'PAGO').reduce((sum, t) => sum + parseFloat(t.monto), 0);
    const totalDeuda = transacciones.filter(t => t.tipo === 'DEUDA').reduce((sum, t) => sum + parseFloat(t.monto), 0);

    return (
        <div style={styles.page}>
            <ToastContainer />

            <div style={styles.header}>
                <div>
                    <h1 style={styles.title}>💰 Módulo Financiero</h1>
                    <p style={styles.subtitle}>RF-25/26 — Gestión de pagos, saldos y comprobantes PDF</p>
                </div>
                <button onClick={() => setShowPagoForm(!showPagoForm)} style={styles.btnPrimary}>
                    {showPagoForm ? 'Cerrar Formulario' : '+ Registrar Transacción'}
                </button>
            </div>

            {/* KPIs */}
            <div style={styles.kpiGrid}>
                <div style={{ ...styles.kpiCard, borderTopColor: '#10b981' }}>
                    <span style={styles.kpiIcon}>💰</span>
                    <div>
                        <span style={styles.kpiLabel}>INGRESOS TOTALES</span>
                        <div style={{ ...styles.kpiValue, color: '#10b981' }}>Bs. {formatMonto(totalIngresos)}</div>
                    </div>
                </div>
                <div style={{ ...styles.kpiCard, borderTopColor: '#ef4444' }}>
                    <span style={styles.kpiIcon}>📋</span>
                    <div>
                        <span style={styles.kpiLabel}>DEUDA ACUMULADA</span>
                        <div style={{ ...styles.kpiValue, color: '#ef4444' }}>Bs. {formatMonto(totalDeuda)}</div>
                    </div>
                </div>
                <div style={{ ...styles.kpiCard, borderTopColor: '#3b82f6' }}>
                    <span style={styles.kpiIcon}>📊</span>
                    <div>
                        <span style={styles.kpiLabel}>BALANCE NETO</span>
                        <div style={{ ...styles.kpiValue, color: '#3b82f6' }}>Bs. {formatMonto(totalIngresos - totalDeuda)}</div>
                    </div>
                </div>
                <div style={{ ...styles.kpiCard, borderTopColor: '#8b5cf6' }}>
                    <span style={styles.kpiIcon}>🧾</span>
                    <div>
                        <span style={styles.kpiLabel}>TRANSACCIONES</span>
                        <div style={styles.kpiValue}>{transacciones.length}</div>
                    </div>
                </div>
            </div>

            {/* Consulta de Saldo por Paciente */}
            <div style={styles.saldoSection}>
                <h3 style={styles.sectionTitle}>🔍 Consultar Saldo de Paciente (T058)</h3>
                <div style={styles.saldoRow}>
                    <select
                        value={selectedPaciente}
                        onChange={e => handleConsultarSaldo(e.target.value)}
                        style={styles.selectPaciente}
                    >
                        <option value="">Seleccionar paciente...</option>
                        {pacientes.map(p => (
                            <option key={p.id} value={p.id}>{p.nombre} (CI: {p.ci})</option>
                        ))}
                    </select>
                    {saldoInfo && (
                        <div style={styles.saldoCard}>
                            <div style={styles.saldoItem}>
                                <span style={styles.saldoLabel}>Paciente</span>
                                <span style={styles.saldoValue}>{saldoInfo.paciente}</span>
                            </div>
                            <div style={styles.saldoItem}>
                                <span style={styles.saldoLabel}>Total Pagado</span>
                                <span style={{ ...styles.saldoValue, color: '#10b981' }}>Bs. {formatMonto(saldoInfo.total_pagado)}</span>
                            </div>
                            <div style={styles.saldoItem}>
                                <span style={styles.saldoLabel}>Deuda Acumulada</span>
                                <span style={{ ...styles.saldoValue, color: '#ef4444' }}>Bs. {formatMonto(saldoInfo.total_deuda_acumulada)}</span>
                            </div>
                            <div style={styles.saldoItem}>
                                <span style={styles.saldoLabel}>Saldo Pendiente</span>
                                <span style={{ ...styles.saldoValue, color: '#f59e0b', fontSize: '24px' }}>Bs. {formatMonto(saldoInfo.saldo_pendiente)}</span>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Formulario de Pago */}
            {showPagoForm && (
                <div style={styles.formCard}>
                    <h3 style={styles.sectionTitle}>💳 Registrar Transacción (T059)</h3>
                    <form onSubmit={handleRegistrarPago} style={styles.formGrid}>
                        <div style={styles.formGroup}>
                            <label style={styles.label}>Paciente *</label>
                            <select
                                value={pagoForm.paciente}
                                onChange={e => setPagoForm({ ...pagoForm, paciente: e.target.value })}
                                style={styles.input}
                                required
                            >
                                <option value="">Seleccionar...</option>
                                {pacientes.map(p => (
                                    <option key={p.id} value={p.id}>{p.nombre}</option>
                                ))}
                            </select>
                        </div>
                        <div style={styles.formGroup}>
                            <label style={styles.label}>Tipo *</label>
                            <select
                                value={pagoForm.tipo}
                                onChange={e => setPagoForm({ ...pagoForm, tipo: e.target.value })}
                                style={styles.input}
                                required
                            >
                                <option value="PAGO">💰 Pago de Sesión</option>
                                <option value="DEUDA">📋 Cargo de Sesión</option>
                                <option value="AJUSTE">⚙️ Ajuste de Saldo</option>
                            </select>
                        </div>
                        <div style={styles.formGroup}>
                            <label style={styles.label}>Monto (Bs.) *</label>
                            <input
                                type="number"
                                step="0.01"
                                min="0"
                                value={pagoForm.monto}
                                onChange={e => setPagoForm({ ...pagoForm, monto: e.target.value })}
                                style={styles.input}
                                placeholder="0.00"
                                required
                            />
                        </div>
                        <div style={styles.formGroup}>
                            <label style={styles.label}>Descripción</label>
                            <input
                                type="text"
                                value={pagoForm.descripcion}
                                onChange={e => setPagoForm({ ...pagoForm, descripcion: e.target.value })}
                                style={styles.input}
                                placeholder="Ej: Pago de sesión del 10/05"
                            />
                        </div>
                        <div style={{ gridColumn: 'span 2', display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
                            <button type="button" onClick={() => setShowPagoForm(false)} style={styles.btnCancel}>Cancelar</button>
                            <button type="submit" style={styles.btnPrimary}>Registrar</button>
                        </div>
                    </form>
                </div>
            )}

            {/* Tabla de Transacciones */}
            <div style={styles.tableCard}>
                <h3 style={{ ...styles.sectionTitle, padding: '24px 24px 0' }}>
                    📊 Historial de Transacciones (RF-26)
                </h3>
                <table style={styles.table}>
                    <thead>
                        <tr style={styles.tableHead}>
                            <th style={styles.th}>ID</th>
                            <th style={styles.th}>Paciente</th>
                            <th style={styles.th}>Tipo</th>
                            <th style={styles.th}>Monto</th>
                            <th style={styles.th}>Fecha</th>
                            <th style={styles.th}>Descripción</th>
                            <th style={{ ...styles.th, textAlign: 'right' }}>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr><td colSpan="7" style={styles.emptyCell}>Cargando transacciones...</td></tr>
                        ) : transacciones.length === 0 ? (
                            <tr><td colSpan="7" style={styles.emptyCell}>No hay transacciones registradas.</td></tr>
                        ) : (
                            transacciones.map(tx => {
                                const tipo = TIPO_COLORS[tx.tipo] || TIPO_COLORS.PAGO;
                                const paciente = pacientes.find(p => p.id === tx.paciente);
                                return (
                                    <tr key={tx.id} style={styles.tr}>
                                        <td style={styles.td}>#{tx.id}</td>
                                        <td style={styles.tdBold}>{paciente?.nombre || `#${tx.paciente}`}</td>
                                        <td style={styles.td}>
                                            <span style={{
                                                backgroundColor: tipo.bg,
                                                color: tipo.color,
                                                padding: '4px 12px',
                                                borderRadius: '8px',
                                                fontSize: '12px',
                                                fontWeight: '700',
                                            }}>
                                                {tipo.icon} {tx.tipo}
                                            </span>
                                        </td>
                                        <td style={{ ...styles.tdBold, color: tx.tipo === 'PAGO' ? '#10b981' : '#ef4444' }}>
                                            Bs. {formatMonto(tx.monto)}
                                        </td>
                                        <td style={styles.td}>{formatFecha(tx.fecha)}</td>
                                        <td style={styles.td}>{tx.descripcion || '—'}</td>
                                        <td style={{ ...styles.td, textAlign: 'right' }}>
                                            {tx.tipo === 'PAGO' && (
                                                <button
                                                    onClick={() => handleDescargarPDF(tx.id)}
                                                    style={styles.btnPDF}
                                                    title="Descargar comprobante PDF"
                                                >
                                                    📄 PDF
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                );
                            })
                        )}
                    </tbody>
                </table>
            </div>

            {/* --- MODAL MOCK DE PASARELA DE PAGOS (RF-25) --- */}
            {(isProcessingPayment || paymentSuccess) && (
                <div style={styles.modalOverlay}>
                    <div style={styles.paymentModal}>
                        {isProcessingPayment ? (
                            <>
                                <div style={styles.spinner}></div>
                                <h3 style={styles.paymentTitle}>Procesando Pago...</h3>
                                <p style={styles.paymentText}>Conectando con la pasarela segura. Por favor no cierre la ventana.</p>
                            </>
                        ) : (
                            <>
                                <div style={styles.successCheck}>✅</div>
                                <h3 style={{...styles.paymentTitle, color: '#10b981'}}>¡Transacción Aprobada!</h3>
                                <p style={styles.paymentText}>El pago se ha registrado correctamente en el sistema.</p>
                            </>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

// ==============================================================================
// ESTILOS
// ==============================================================================
const styles = {
    page: { padding: '32px 40px', backgroundColor: '#f1f5f9', minHeight: '100vh', fontFamily: '"Inter", sans-serif' },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' },
    title: { fontSize: '28px', fontWeight: '800', color: '#0f172a', margin: 0 },
    subtitle: { fontSize: '14px', color: '#64748b', marginTop: '4px' },
    btnPrimary: { backgroundColor: '#2563eb', color: 'white', padding: '12px 24px', borderRadius: '12px', border: 'none', fontWeight: '700', fontSize: '14px', cursor: 'pointer', boxShadow: '0 4px 12px rgba(37,99,235,0.3)' },
    btnCancel: { backgroundColor: '#f1f5f9', color: '#475569', padding: '12px 24px', borderRadius: '12px', border: 'none', fontWeight: '600', cursor: 'pointer' },
    btnPDF: { padding: '6px 14px', backgroundColor: '#fef3c7', color: '#d97706', borderRadius: '8px', border: '1px solid #fde68a', cursor: 'pointer', fontWeight: '700', fontSize: '12px' },
    kpiGrid: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' },
    kpiCard: { backgroundColor: 'white', borderRadius: '16px', padding: '24px', borderTop: '4px solid', display: 'flex', alignItems: 'center', gap: '16px', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' },
    kpiIcon: { fontSize: '32px' },
    kpiLabel: { fontSize: '11px', fontWeight: '700', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px' },
    kpiValue: { fontSize: '22px', fontWeight: '800', color: '#0f172a', marginTop: '4px' },
    saldoSection: { backgroundColor: 'white', borderRadius: '20px', padding: '24px', border: '1px solid #e2e8f0', marginBottom: '24px' },
    sectionTitle: { fontSize: '16px', fontWeight: '700', color: '#0f172a', marginBottom: '16px' },
    saldoRow: { display: 'flex', gap: '24px', alignItems: 'flex-start' },
    selectPaciente: { padding: '12px 16px', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '14px', minWidth: '280px', cursor: 'pointer' },
    saldoCard: { flex: 1, display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' },
    saldoItem: { display: 'flex', flexDirection: 'column', gap: '4px' },
    saldoLabel: { fontSize: '11px', fontWeight: '700', color: '#94a3b8', textTransform: 'uppercase' },
    saldoValue: { fontSize: '16px', fontWeight: '800', color: '#0f172a' },
    formCard: { backgroundColor: 'white', padding: '28px', borderRadius: '20px', border: '1px solid #e2e8f0', marginBottom: '24px' },
    formGrid: { display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' },
    formGroup: { marginBottom: '4px' },
    label: { display: 'block', fontSize: '12px', fontWeight: '700', color: '#64748b', marginBottom: '8px', textTransform: 'uppercase' },
    input: { width: '100%', padding: '12px 16px', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '14px', outline: 'none', boxSizing: 'border-box', fontFamily: 'inherit' },
    tableCard: { backgroundColor: 'white', borderRadius: '20px', border: '1px solid #e2e8f0', overflow: 'hidden', boxShadow: '0 4px 24px rgba(0,0,0,0.06)' },
    table: { width: '100%', borderCollapse: 'collapse' },
    tableHead: { borderBottom: '2px solid #f1f5f9' },
    th: { padding: '16px 20px', fontSize: '12px', fontWeight: '700', color: '#64748b', textTransform: 'uppercase', textAlign: 'left' },
    tr: { borderBottom: '1px solid #f1f5f9' },
    td: { padding: '16px 20px', fontSize: '14px', color: '#64748b' },
    tdBold: { padding: '16px 20px', fontSize: '14px', color: '#0f172a', fontWeight: '700' },
    emptyCell: { padding: '48px', textAlign: 'center', color: '#94a3b8' },
    modalOverlay: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(15,23,42,0.6)', backdropFilter: 'blur(4px)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 9999 },
    paymentModal: { backgroundColor: 'white', padding: '40px', borderRadius: '24px', width: '360px', textAlign: 'center', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)', animation: 'fadeIn 0.3s ease-out' },
    spinner: { width: '48px', height: '48px', border: '5px solid #e2e8f0', borderTopColor: '#3b82f6', borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto 24px' },
    successCheck: { fontSize: '64px', marginBottom: '16px', animation: 'fadeIn 0.5s ease-out' },
    paymentTitle: { fontSize: '20px', fontWeight: '800', color: '#0f172a', margin: '0 0 8px 0' },
    paymentText: { fontSize: '14px', color: '#64748b', margin: 0, lineHeight: 1.5 },
};

export default Finanzas;
