// ==============================================================================
// [SPRINT 2 - RF-06/RF-07 / CU11/CU12/CU13] Gestión de Citas
// CRUD completo: Crear, Modificar, Cancelar, Completar citas.
// T030: Manejo de error 400 por colisión de horario.
// ==============================================================================
import React, { useEffect, useState, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import citaService from '../services/citaService';
import pacienteService from '../services/pacienteService';
import apiClient from '../api/axiosConfig';
import { useToast } from '../components/Toast';

const ESTADOS_BADGE = {
    PENDIENTE: { bg: '#dbeafe', color: '#1d4ed8', label: '⏳ Pendiente' },
    COMPLETADA: { bg: '#dcfce7', color: '#15803d', label: '✅ Completada' },
    CANCELADA: { bg: '#fee2e2', color: '#dc2626', label: '❌ Cancelada' },
};

const GestionCitas = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { user } = useAuth();
    const { showToast, ToastContainer } = useToast();

    const [citas, setCitas] = useState([]);
    const [pacientes, setPacientes] = useState([]);
    const [psicologos, setPsicologos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editingCita, setEditingCita] = useState(null);
    const [filtroEstado, setFiltroEstado] = useState('');
    const [busqueda, setBusqueda] = useState('');

    // Form state
    const [form, setForm] = useState({
        paciente: '',
        psicologo: '',
        fecha_hora: '',
        motivo: '',
    });

    const fetchData = useCallback(async () => {
        try {
            setLoading(true);
            const [citasData, pacientesData, psicologosData] = await Promise.all([
                citaService.getCitas({ estado: filtroEstado || undefined }),
                pacienteService.getPacientes(),
                apiClient.get('psicologos/').then(r => r.data),
            ]);
            setCitas(Array.isArray(citasData) ? citasData : []);
            setPacientes(Array.isArray(pacientesData) ? pacientesData : []);
            setPsicologos(Array.isArray(psicologosData) ? psicologosData : []);
        } catch (err) {
            console.error(err);
            showToast('Error cargando datos', 'error');
        } finally {
            setLoading(false);
        }
    }, [filtroEstado, showToast]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    // Pre-fill date if navigated from Agenda
    useEffect(() => {
        if (location.state?.preselectedDate) {
            const d = new Date(location.state.preselectedDate);
            const localISO = new Date(d.getTime() - d.getTimezoneOffset() * 60000)
                .toISOString().slice(0, 16);
            setForm(prev => ({ ...prev, fecha_hora: localISO }));
            setShowModal(true);
        }
    }, [location.state]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (editingCita) {
                await citaService.actualizarCita(editingCita.id, form);
                showToast('Cita actualizada exitosamente', 'success');
            } else {
                await citaService.crearCita(form);
                showToast('Cita programada exitosamente', 'success');
            }
            setShowModal(false);
            setEditingCita(null);
            setForm({ paciente: '', psicologo: '', fecha_hora: '', motivo: '' });
            fetchData();
        } catch (err) {
            const errorData = err.response?.data;
            if (err.response?.status === 400) {
                // T030: Capturar colisión de horario
                const msg = errorData?.fecha_hora?.[0]
                    || errorData?.detail
                    || 'El psicólogo ya tiene una cita en ese horario.';
                showToast(msg, 'warning');
            } else {
                showToast('Error al guardar la cita', 'error');
            }
        }
    };

    const handleCancel = async (id) => {
        if (window.confirm('¿Está seguro de cancelar esta cita? Esta acción no se puede deshacer.')) {
            try {
                await citaService.cancelarCita(id);
                showToast('Cita cancelada exitosamente', 'success');
                fetchData();
            } catch {
                showToast('Error al cancelar la cita', 'error');
            }
        }
    };

    const handleComplete = async (id) => {
        try {
            await citaService.completarCita(id);
            showToast('Cita marcada como completada', 'success');
            fetchData();
        } catch {
            showToast('Error al completar la cita', 'error');
        }
    };

    const openEdit = (cita) => {
        setEditingCita(cita);
        const d = new Date(cita.fecha_hora);
        const localISO = new Date(d.getTime() - d.getTimezoneOffset() * 60000)
            .toISOString().slice(0, 16);
        setForm({
            paciente: cita.paciente,
            psicologo: cita.psicologo,
            fecha_hora: localISO,
            motivo: cita.motivo || '',
        });
        setShowModal(true);
    };

    const citasFiltradas = citas.filter(c => {
        if (busqueda) {
            const term = busqueda.toLowerCase();
            return (c.paciente_nombre || '').toLowerCase().includes(term)
                || (c.psicologo_nombre || '').toLowerCase().includes(term);
        }
        return true;
    });

    const formatFecha = (iso) => {
        const d = new Date(iso);
        return d.toLocaleDateString('es-BO', {
            weekday: 'short', day: '2-digit', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    };

    return (
        <div style={styles.page}>
            <ToastContainer />

            {/* Header */}
            <div style={styles.header}>
                <div>
                    <h1 style={styles.title}>🗓️ Gestión de Citas</h1>
                    <p style={styles.subtitle}>RF-06 / RF-07 — Programación, modificación y cancelación de citas</p>
                </div>
                <div style={styles.headerActions}>
                    <button onClick={() => navigate('/agenda')} style={styles.btnOutline}>
                        📅 Ver Calendario
                    </button>
                    <button onClick={() => { setEditingCita(null); setForm({ paciente: '', psicologo: '', fecha_hora: '', motivo: '' }); setShowModal(true); }} style={styles.btnPrimary}>
                        + Nueva Cita
                    </button>
                </div>
            </div>

            {/* Filtros */}
            <div style={styles.filterBar}>
                <input
                    type="text"
                    placeholder="🔍 Buscar por paciente o psicólogo..."
                    value={busqueda}
                    onChange={(e) => setBusqueda(e.target.value)}
                    style={styles.searchInput}
                />
                <select
                    value={filtroEstado}
                    onChange={(e) => setFiltroEstado(e.target.value)}
                    style={styles.selectFilter}
                >
                    <option value="">Todos los estados</option>
                    <option value="PENDIENTE">⏳ Pendiente</option>
                    <option value="COMPLETADA">✅ Completada</option>
                    <option value="CANCELADA">❌ Cancelada</option>
                </select>
            </div>

            {/* Stats */}
            <div style={styles.statsRow}>
                <div style={{ ...styles.statCard, borderLeftColor: '#3b82f6' }}>
                    <span style={styles.statNumber}>{citas.filter(c => c.estado === 'PENDIENTE').length}</span>
                    <span style={styles.statLabel}>Pendientes</span>
                </div>
                <div style={{ ...styles.statCard, borderLeftColor: '#10b981' }}>
                    <span style={styles.statNumber}>{citas.filter(c => c.estado === 'COMPLETADA').length}</span>
                    <span style={styles.statLabel}>Completadas</span>
                </div>
                <div style={{ ...styles.statCard, borderLeftColor: '#ef4444' }}>
                    <span style={styles.statNumber}>{citas.filter(c => c.estado === 'CANCELADA').length}</span>
                    <span style={styles.statLabel}>Canceladas</span>
                </div>
                <div style={{ ...styles.statCard, borderLeftColor: '#8b5cf6' }}>
                    <span style={styles.statNumber}>{citas.length}</span>
                    <span style={styles.statLabel}>Total</span>
                </div>
            </div>

            {/* Tabla */}
            <div style={styles.tableCard}>
                <table style={styles.table}>
                    <thead>
                        <tr style={styles.tableHead}>
                            <th style={styles.th}>Paciente</th>
                            <th style={styles.th}>Psicólogo</th>
                            <th style={styles.th}>Fecha y Hora</th>
                            <th style={styles.th}>Motivo</th>
                            <th style={styles.th}>Estado</th>
                            <th style={{ ...styles.th, textAlign: 'right' }}>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr><td colSpan="6" style={styles.emptyCell}>Cargando citas...</td></tr>
                        ) : citasFiltradas.length === 0 ? (
                            <tr><td colSpan="6" style={styles.emptyCell}>No hay citas registradas.</td></tr>
                        ) : (
                            citasFiltradas.map(cita => {
                                const badge = ESTADOS_BADGE[cita.estado] || ESTADOS_BADGE.PENDIENTE;
                                return (
                                    <tr key={cita.id} style={styles.tr}>
                                        <td style={styles.tdBold}>{cita.paciente_nombre || `Paciente #${cita.paciente}`}</td>
                                        <td style={styles.td}>{cita.psicologo_nombre || `Dr. #${cita.psicologo}`}</td>
                                        <td style={styles.td}>{formatFecha(cita.fecha_hora)}</td>
                                        <td style={styles.td}>{cita.motivo || '—'}</td>
                                        <td style={styles.td}>
                                            <span style={{
                                                backgroundColor: badge.bg,
                                                color: badge.color,
                                                padding: '4px 12px',
                                                borderRadius: '8px',
                                                fontSize: '12px',
                                                fontWeight: '700',
                                            }}>
                                                {badge.label}
                                            </span>
                                        </td>
                                        <td style={{ ...styles.td, textAlign: 'right' }}>
                                            {cita.estado === 'PENDIENTE' && (
                                                <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                                                    <button onClick={() => openEdit(cita)} style={styles.btnSmall} title="Reprogramar">✏️</button>
                                                    <button onClick={() => handleComplete(cita.id)} style={{ ...styles.btnSmall, backgroundColor: '#dcfce7', color: '#15803d' }} title="Completar">✅</button>
                                                    <button onClick={() => handleCancel(cita.id)} style={{ ...styles.btnSmall, backgroundColor: '#fee2e2', color: '#dc2626' }} title="Cancelar">🗑️</button>
                                                </div>
                                            )}
                                        </td>
                                    </tr>
                                );
                            })
                        )}
                    </tbody>
                </table>
            </div>

            {/* Modal Crear/Editar */}
            {showModal && (
                <div style={styles.overlay} onClick={() => setShowModal(false)}>
                    <div style={styles.modal} onClick={e => e.stopPropagation()}>
                        <h2 style={styles.modalTitle}>
                            {editingCita ? '✏️ Reprogramar Cita' : '🗓️ Programar Nueva Cita'}
                        </h2>
                        <form onSubmit={handleSubmit}>
                            <div style={styles.formGroup}>
                                <label style={styles.label}>Paciente *</label>
                                <select
                                    value={form.paciente}
                                    onChange={e => setForm({ ...form, paciente: e.target.value })}
                                    style={styles.input}
                                    required
                                >
                                    <option value="">Seleccionar paciente...</option>
                                    {pacientes.map(p => (
                                        <option key={p.id} value={p.id}>{p.nombre} (CI: {p.ci})</option>
                                    ))}
                                </select>
                            </div>
                            <div style={styles.formGroup}>
                                <label style={styles.label}>Psicólogo *</label>
                                <select
                                    value={form.psicologo}
                                    onChange={e => setForm({ ...form, psicologo: e.target.value })}
                                    style={styles.input}
                                    required
                                >
                                    <option value="">Seleccionar psicólogo...</option>
                                    {psicologos.map(p => (
                                        <option key={p.id} value={p.id}>
                                            {p.first_name} {p.last_name} — {p.especialidad || 'General'}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div style={styles.formGroup}>
                                <label style={styles.label}>Fecha y Hora *</label>
                                <input
                                    type="datetime-local"
                                    value={form.fecha_hora}
                                    onChange={e => setForm({ ...form, fecha_hora: e.target.value })}
                                    style={styles.input}
                                    required
                                />
                            </div>
                            <div style={styles.formGroup}>
                                <label style={styles.label}>Motivo de Consulta</label>
                                <textarea
                                    value={form.motivo}
                                    onChange={e => setForm({ ...form, motivo: e.target.value })}
                                    style={{ ...styles.input, minHeight: '80px', resize: 'vertical' }}
                                    placeholder="Breve descripción del motivo de la cita..."
                                />
                            </div>
                            <div style={styles.modalActions}>
                                <button type="button" onClick={() => setShowModal(false)} style={styles.btnCancel}>
                                    Cancelar
                                </button>
                                <button type="submit" style={styles.btnPrimary}>
                                    {editingCita ? 'Actualizar Cita' : 'Programar Cita'}
                                </button>
                            </div>
                        </form>
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
    headerActions: { display: 'flex', gap: '12px' },
    btnPrimary: { backgroundColor: '#2563eb', color: 'white', padding: '12px 24px', borderRadius: '12px', border: 'none', fontWeight: '700', fontSize: '14px', cursor: 'pointer', boxShadow: '0 4px 12px rgba(37,99,235,0.3)' },
    btnOutline: { backgroundColor: 'white', color: '#475569', padding: '12px 20px', borderRadius: '12px', border: '1px solid #e2e8f0', fontWeight: '600', fontSize: '14px', cursor: 'pointer' },
    btnCancel: { backgroundColor: '#f1f5f9', color: '#475569', padding: '12px 24px', borderRadius: '12px', border: 'none', fontWeight: '600', cursor: 'pointer' },
    btnSmall: { padding: '6px 10px', backgroundColor: '#f1f5f9', border: '1px solid #e2e8f0', borderRadius: '8px', cursor: 'pointer', fontSize: '14px' },
    filterBar: { display: 'flex', gap: '16px', marginBottom: '24px' },
    searchInput: { flex: 1, padding: '12px 20px', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '14px', outline: 'none', backgroundColor: 'white' },
    selectFilter: { padding: '12px 20px', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '14px', backgroundColor: 'white', cursor: 'pointer', minWidth: '200px' },
    statsRow: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' },
    statCard: { backgroundColor: 'white', borderRadius: '16px', padding: '20px 24px', borderLeft: '4px solid', display: 'flex', flexDirection: 'column', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' },
    statNumber: { fontSize: '28px', fontWeight: '800', color: '#0f172a' },
    statLabel: { fontSize: '13px', color: '#64748b', fontWeight: '600', marginTop: '4px' },
    tableCard: { backgroundColor: 'white', borderRadius: '20px', border: '1px solid #e2e8f0', overflow: 'hidden', boxShadow: '0 4px 24px rgba(0,0,0,0.06)' },
    table: { width: '100%', borderCollapse: 'collapse' },
    tableHead: { borderBottom: '2px solid #f1f5f9' },
    th: { padding: '16px 20px', fontSize: '12px', fontWeight: '700', color: '#64748b', textTransform: 'uppercase', textAlign: 'left' },
    tr: { borderBottom: '1px solid #f1f5f9', transition: 'background 0.15s' },
    td: { padding: '16px 20px', fontSize: '14px', color: '#64748b' },
    tdBold: { padding: '16px 20px', fontSize: '14px', color: '#0f172a', fontWeight: '700' },
    emptyCell: { padding: '48px', textAlign: 'center', color: '#94a3b8', fontSize: '14px' },
    overlay: { position: 'fixed', inset: 0, backgroundColor: 'rgba(15,23,42,0.6)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999 },
    modal: { backgroundColor: 'white', borderRadius: '24px', padding: '40px', width: '520px', maxWidth: '95vw', boxShadow: '0 40px 100px rgba(0,0,0,0.3)', maxHeight: '90vh', overflowY: 'auto' },
    modalTitle: { fontSize: '22px', fontWeight: '800', color: '#0f172a', marginBottom: '32px' },
    modalActions: { display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '32px' },
    formGroup: { marginBottom: '20px' },
    label: { display: 'block', fontSize: '13px', fontWeight: '700', color: '#475569', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' },
    input: { width: '100%', padding: '12px 16px', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '14px', outline: 'none', boxSizing: 'border-box', transition: 'border 0.2s', fontFamily: 'inherit' },
};

export default GestionCitas;
