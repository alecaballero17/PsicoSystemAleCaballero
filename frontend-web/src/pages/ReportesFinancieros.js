// ==============================================================================
// [SPRINT 2 - RF-27] Reportes Financieros — Resúmenes económicos por período
// Incluye generación de audio TTS para accesibilidad.
// ==============================================================================
import React, { useState } from 'react';
import finanzaService from '../services/finanzaService';
import { useToast } from '../components/Toast';

const ReportesFinancieros = () => {
    const { showToast, ToastContainer } = useToast();

    const [fechaInicio, setFechaInicio] = useState('');
    const [fechaFin, setFechaFin] = useState('');
    const [generarAudio, setGenerarAudio] = useState(true);
    const [reporte, setReporte] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleGenerarReporte = async (e) => {
        e.preventDefault();
        if (!fechaInicio || !fechaFin) {
            showToast('Debe seleccionar ambas fechas', 'warning');
            return;
        }
        try {
            setLoading(true);
            const data = await finanzaService.generarReporte(fechaInicio, fechaFin, generarAudio);
            setReporte(data);
            showToast('Reporte generado exitosamente', 'success');
        } catch (err) {
            const msg = err.response?.data?.error || 'Error al generar el reporte';
            showToast(msg, 'error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.page}>
            <ToastContainer />

            <div style={styles.header}>
                <h1 style={styles.title}>📊 Reportes Económicos</h1>
                <p style={styles.subtitle}>RF-27 — Resúmenes de ingresos y estados de cuenta por período</p>
            </div>

            {/* Formulario */}
            <div style={styles.formCard}>
                <h3 style={styles.sectionTitle}>🗓️ Seleccionar Período de Análisis</h3>
                <form onSubmit={handleGenerarReporte} style={styles.formRow}>
                    <div style={styles.formGroup}>
                        <label style={styles.label}>Fecha Inicio</label>
                        <input
                            type="date"
                            value={fechaInicio}
                            onChange={e => setFechaInicio(e.target.value)}
                            style={styles.input}
                            required
                        />
                    </div>
                    <div style={styles.formGroup}>
                        <label style={styles.label}>Fecha Fin</label>
                        <input
                            type="date"
                            value={fechaFin}
                            onChange={e => setFechaFin(e.target.value)}
                            style={styles.input}
                            required
                        />
                    </div>
                    <div style={styles.formGroup}>
                        <label style={styles.label}>Audio TTS</label>
                        <div style={styles.checkboxRow}>
                            <input
                                type="checkbox"
                                checked={generarAudio}
                                onChange={e => setGenerarAudio(e.target.checked)}
                                id="audioCheck"
                            />
                            <label htmlFor="audioCheck" style={{ fontSize: '14px', color: '#475569', cursor: 'pointer' }}>
                                Generar audio del reporte
                            </label>
                        </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'flex-end' }}>
                        <button type="submit" style={styles.btnPrimary} disabled={loading}>
                            {loading ? '⏳ Generando...' : '📊 Generar Reporte'}
                        </button>
                    </div>
                </form>
            </div>

            {/* Resultado del Reporte */}
            {reporte && (
                <div style={styles.reporteCard}>
                    <div style={styles.reporteHeader}>
                        <h3 style={styles.reporteTitulo}>📋 Reporte Ejecutivo</h3>
                        <span style={styles.reportePeriodo}>
                            {reporte.fecha_inicio} → {reporte.fecha_fin}
                        </span>
                    </div>

                    <div style={styles.reporteTexto}>
                        {reporte.texto}
                    </div>

                    {/* Reproductor de Audio */}
                    {reporte.audio_url && (
                        <div style={styles.audioSection}>
                            <h4 style={styles.audioLabel}>🔊 Audio del Reporte (gTTS)</h4>
                            <audio
                                controls
                                src={reporte.audio_url}
                                style={styles.audioPlayer}
                            >
                                Tu navegador no soporta el elemento de audio.
                            </audio>
                            <small style={styles.audioHelp}>
                                Generado automáticamente con Google Text-to-Speech en español
                            </small>
                        </div>
                    )}
                </div>
            )}

            {/* Accesos Rápidos */}
            <div style={styles.quickAccess}>
                <div style={styles.quickCard} onClick={() => {
                    const hoy = new Date();
                    const inicio = new Date(hoy.getFullYear(), hoy.getMonth(), 1).toISOString().split('T')[0];
                    const fin = hoy.toISOString().split('T')[0];
                    setFechaInicio(inicio);
                    setFechaFin(fin);
                }}>
                    <span style={styles.quickIcon}>📅</span>
                    <span style={styles.quickText}>Este Mes</span>
                </div>
                <div style={styles.quickCard} onClick={() => {
                    const hoy = new Date();
                    const inicio = new Date(hoy.getFullYear(), 0, 1).toISOString().split('T')[0];
                    const fin = hoy.toISOString().split('T')[0];
                    setFechaInicio(inicio);
                    setFechaFin(fin);
                }}>
                    <span style={styles.quickIcon}>📆</span>
                    <span style={styles.quickText}>Este Año</span>
                </div>
                <div style={styles.quickCard} onClick={() => {
                    const hoy = new Date();
                    const hace30 = new Date(hoy.getTime() - 30 * 24 * 60 * 60 * 1000);
                    setFechaInicio(hace30.toISOString().split('T')[0]);
                    setFechaFin(hoy.toISOString().split('T')[0]);
                }}>
                    <span style={styles.quickIcon}>⏰</span>
                    <span style={styles.quickText}>Últimos 30 días</span>
                </div>
            </div>
        </div>
    );
};

const styles = {
    page: { padding: '32px 40px', backgroundColor: '#f1f5f9', minHeight: '100vh', fontFamily: '"Inter", sans-serif' },
    header: { marginBottom: '24px' },
    title: { fontSize: '28px', fontWeight: '800', color: '#0f172a', margin: 0 },
    subtitle: { fontSize: '14px', color: '#64748b', marginTop: '4px' },
    formCard: { backgroundColor: 'white', padding: '28px', borderRadius: '20px', border: '1px solid #e2e8f0', marginBottom: '24px' },
    sectionTitle: { fontSize: '16px', fontWeight: '700', color: '#0f172a', marginBottom: '20px' },
    formRow: { display: 'flex', gap: '20px', alignItems: 'flex-start', flexWrap: 'wrap' },
    formGroup: { display: 'flex', flexDirection: 'column', minWidth: '200px' },
    label: { fontSize: '12px', fontWeight: '700', color: '#64748b', marginBottom: '8px', textTransform: 'uppercase' },
    input: { padding: '12px 16px', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '14px', outline: 'none' },
    checkboxRow: { display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 0' },
    btnPrimary: { backgroundColor: '#2563eb', color: 'white', padding: '12px 28px', borderRadius: '12px', border: 'none', fontWeight: '700', fontSize: '14px', cursor: 'pointer', boxShadow: '0 4px 12px rgba(37,99,235,0.3)', whiteSpace: 'nowrap' },
    reporteCard: { backgroundColor: 'white', borderRadius: '20px', border: '1px solid #e2e8f0', overflow: 'hidden', marginBottom: '24px', boxShadow: '0 4px 24px rgba(0,0,0,0.06)' },
    reporteHeader: { padding: '24px 28px', borderBottom: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
    reporteTitulo: { fontSize: '18px', fontWeight: '800', color: '#0f172a', margin: 0 },
    reportePeriodo: { fontSize: '13px', fontWeight: '600', color: '#3b82f6', backgroundColor: '#eff6ff', padding: '6px 14px', borderRadius: '8px' },
    reporteTexto: { padding: '28px', fontSize: '15px', color: '#475569', lineHeight: '1.8', whiteSpace: 'pre-wrap' },
    audioSection: { padding: '0 28px 28px', borderTop: '1px solid #f1f5f9', paddingTop: '20px' },
    audioLabel: { fontSize: '14px', fontWeight: '700', color: '#0f172a', marginBottom: '12px' },
    audioPlayer: { width: '100%', borderRadius: '12px' },
    audioHelp: { display: 'block', marginTop: '8px', fontSize: '12px', color: '#94a3b8' },
    quickAccess: { display: 'flex', gap: '16px' },
    quickCard: { flex: 1, backgroundColor: 'white', padding: '20px', borderRadius: '16px', border: '1px solid #e2e8f0', display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer', transition: 'all 0.2s' },
    quickIcon: { fontSize: '24px' },
    quickText: { fontSize: '14px', fontWeight: '700', color: '#475569' },
};

export default ReportesFinancieros;
