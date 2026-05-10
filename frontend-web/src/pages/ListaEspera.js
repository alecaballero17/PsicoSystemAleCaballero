// ==============================================================================
// [SPRINT 2 - T031] Lista de Espera — Pacientes ordenados por prioridad
// Permite agregar pacientes urgentes cuando no hay cupo disponible.
// ==============================================================================
import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import citaService from '../services/citaService';
import pacienteService from '../services/pacienteService';
import { useToast } from '../components/Toast';

const PRIORIDAD_CONFIG = {
    1: { label: 'ALTA', bg: '#fee2e2', color: '#dc2626', icon: '🔴' },
    2: { label: 'MEDIA', bg: '#fef3c7', color: '#d97706', icon: '🟡' },
    3: { label: 'BAJA', bg: '#dcfce7', color: '#15803d', icon: '🟢' },
};

const ListaEspera = () => {
    const navigate = useNavigate();
    const { showToast, ToastContainer } = useToast();

    const [listaEspera, setListaEspera] = useState([]);
    const [pacientes, setPacientes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);

    const [form, setForm] = useState({
        paciente: '',
        prioridad: 2,
        observacion: '',
    });

    const fetchData = useCallback(async () => {
        try {
            setLoading(true);
            const [esperaData, pacData] = await Promise.all([
                citaService.getListaEspera(),
                pacienteService.getPacientes(),
            ]);
            setListaEspera(Array.isArray(esperaData) ? esperaData : []);
            setPacientes(Array.isArray(pacData) ? pacData : []);
        } catch {
            showToast('Error cargando lista de espera', 'error');
        } finally {
            setLoading(false);
        }
    }, [showToast]);

    useEffect(() => { fetchData(); }, [fetchData]);

    const handleAgregar = async (e) => {
        e.preventDefault();
        try {
            await citaService.agregarEspera(form);
            showToast('Paciente agregado a la lista de espera', 'success');
            setForm({ paciente: '', prioridad: 2, observacion: '' });
            setShowForm(false);
            fetchData();
        } catch (err) {
            showToast('Error al agregar a la lista de espera', 'error');
        }
    };

    const handleEliminar = async (id) => {
        if (window.confirm('¿Desea remover al paciente de la lista de espera?')) {
            try {
                await citaService.eliminarEspera(id);
                showToast('Paciente removido de la lista de espera', 'success');
                fetchData();
            } catch {
                showToast('Error al eliminar', 'error');
            }
        }
    };

    const formatFecha = (iso) => new Date(iso).toLocaleDateString('es-BO', {
        day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
    });

    return (
        <div style={styles.page}>
            <ToastContainer />

            <div style={styles.header}>
                <div>
                    <h1 style={styles.title}>⏳ Lista de Espera</h1>
                    <p style={styles.subtitle}>T031 — Pacientes que necesitan cita urgente, ordenados por prioridad</p>
                </div>
                <div style={styles.headerActions}>
                    <button onClick={() => navigate('/gestion-citas')} style={styles.btnOutline}>
                        🗓️ Ir a Citas
                    </button>
                    <button onClick={() => setShowForm(!showForm)} style={styles.btnPrimary}>
                        {showForm ? 'Cerrar' : '+ Agregar Paciente'}
                    </button>
                </div>
            </div>

            {/* Stats */}
            <div style={styles.statsRow}>
                {Object.entries(PRIORIDAD_CONFIG).map(([key, config]) => {
                    const count = listaEspera.filter(e => e.prioridad === parseInt(key)).length;
                    return (
                        <div key={key} style={{ ...styles.statCard, borderLeftColor: config.color }}>
                            <span style={styles.statIcon}>{config.icon}</span>
                            <div>
                                <span style={styles.statNumber}>{count}</span>
                                <span style={styles.statLabel}>Prioridad {config.label}</span>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Formulario */}
            {showForm && (
                <div style={styles.formCard}>
                    <h3 style={styles.sectionTitle}>Agregar a Lista de Espera</h3>
                    <form onSubmit={handleAgregar} style={styles.formRow}>
                        <div style={styles.formGroup}>
                            <label style={styles.label}>Paciente *</label>
                            <select
                                value={form.paciente}
                                onChange={e => setForm({ ...form, paciente: e.target.value })}
                                style={styles.input}
                                required
                            >
                                <option value="">Seleccionar...</option>
                                {pacientes.map(p => (
                                    <option key={p.id} value={p.id}>{p.nombre} (CI: {p.ci})</option>
                                ))}
                            </select>
                        </div>
                        <div style={styles.formGroup}>
                            <label style={styles.label}>Prioridad *</label>
                            <select
                                value={form.prioridad}
                                onChange={e => setForm({ ...form, prioridad: parseInt(e.target.value) })}
                                style={styles.input}
                                required
                            >
                                <option value={1}>🔴 Alta — Urgente</option>
                                <option value={2}>🟡 Media — Normal</option>
                                <option value={3}>🟢 Baja — No urgente</option>
                            </select>
                        </div>
                        <div style={{ ...styles.formGroup, flex: 2 }}>
                            <label style={styles.label}>Observación</label>
                            <input
                                type="text"
                                value={form.observacion}
                                onChange={e => setForm({ ...form, observacion: e.target.value })}
                                style={styles.input}
                                placeholder="Motivo de la espera..."
                            />
                        </div>
                        <div style={{ display: 'flex', alignItems: 'flex-end' }}>
                            <button type="submit" style={styles.btnPrimary}>Agregar</button>
                        </div>
                    </form>
                </div>
            )}

            {/* Tabla */}
            <div style={styles.tableCard}>
                <table style={styles.table}>
                    <thead>
                        <tr style={styles.tableHead}>
                            <th style={styles.th}>Prioridad</th>
                            <th style={styles.th}>Paciente</th>
                            <th style={styles.th}>Observación</th>
                            <th style={styles.th}>Fecha Registro</th>
                            <th style={{ ...styles.th, textAlign: 'right' }}>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr><td colSpan="5" style={styles.emptyCell}>Cargando lista de espera...</td></tr>
                        ) : listaEspera.length === 0 ? (
                            <tr><td colSpan="5" style={styles.emptyCell}>
                                No hay pacientes en lista de espera. 🎉
                            </td></tr>
                        ) : (
                            listaEspera.map(item => {
                                const prio = PRIORIDAD_CONFIG[item.prioridad] || PRIORIDAD_CONFIG[2];
                                return (
                                    <tr key={item.id} style={styles.tr}>
                                        <td style={styles.td}>
                                            <span style={{
                                                backgroundColor: prio.bg,
                                                color: prio.color,
                                                padding: '6px 14px',
                                                borderRadius: '8px',
                                                fontSize: '12px',
                                                fontWeight: '700',
                                            }}>
                                                {prio.icon} {prio.label}
                                            </span>
                                        </td>
                                        <td style={styles.tdBold}>
                                            {item.paciente_nombre || `Paciente #${item.paciente}`}
                                        </td>
                                        <td style={styles.td}>{item.observacion || '—'}</td>
                                        <td style={styles.td}>{formatFecha(item.fecha_registro)}</td>
                                        <td style={{ ...styles.td, textAlign: 'right' }}>
                                            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                                                <button
                                                    onClick={() => navigate('/gestion-citas')}
                                                    style={styles.btnAgendarSmall}
                                                    title="Agendar cita"
                                                >
                                                    🗓️ Agendar
                                                </button>
                                                <button
                                                    onClick={() => handleEliminar(item.id)}
                                                    style={styles.btnDeleteSmall}
                                                    title="Remover"
                                                >
                                                    🗑️
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                );
                            })
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

const styles = {
    page: { padding: '32px 40px', backgroundColor: '#f1f5f9', minHeight: '100vh', fontFamily: '"Inter", sans-serif' },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' },
    title: { fontSize: '28px', fontWeight: '800', color: '#0f172a', margin: 0 },
    subtitle: { fontSize: '14px', color: '#64748b', marginTop: '4px' },
    headerActions: { display: 'flex', gap: '12px' },
    btnPrimary: { backgroundColor: '#2563eb', color: 'white', padding: '12px 24px', borderRadius: '12px', border: 'none', fontWeight: '700', fontSize: '14px', cursor: 'pointer', boxShadow: '0 4px 12px rgba(37,99,235,0.3)' },
    btnOutline: { backgroundColor: 'white', color: '#475569', padding: '12px 20px', borderRadius: '12px', border: '1px solid #e2e8f0', fontWeight: '600', fontSize: '14px', cursor: 'pointer' },
    statsRow: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' },
    statCard: { backgroundColor: 'white', borderRadius: '16px', padding: '20px 24px', borderLeft: '4px solid', display: 'flex', alignItems: 'center', gap: '16px' },
    statIcon: { fontSize: '28px' },
    statNumber: { fontSize: '28px', fontWeight: '800', color: '#0f172a', display: 'block' },
    statLabel: { fontSize: '12px', color: '#64748b', fontWeight: '600' },
    formCard: { backgroundColor: 'white', padding: '24px', borderRadius: '20px', border: '1px solid #e2e8f0', marginBottom: '24px' },
    sectionTitle: { fontSize: '16px', fontWeight: '700', color: '#0f172a', marginBottom: '16px' },
    formRow: { display: 'flex', gap: '16px', alignItems: 'flex-start', flexWrap: 'wrap' },
    formGroup: { flex: 1, minWidth: '180px' },
    label: { display: 'block', fontSize: '12px', fontWeight: '700', color: '#64748b', marginBottom: '8px', textTransform: 'uppercase' },
    input: { width: '100%', padding: '12px 16px', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '14px', outline: 'none', boxSizing: 'border-box' },
    tableCard: { backgroundColor: 'white', borderRadius: '20px', border: '1px solid #e2e8f0', overflow: 'hidden', boxShadow: '0 4px 24px rgba(0,0,0,0.06)' },
    table: { width: '100%', borderCollapse: 'collapse' },
    tableHead: { borderBottom: '2px solid #f1f5f9' },
    th: { padding: '16px 20px', fontSize: '12px', fontWeight: '700', color: '#64748b', textTransform: 'uppercase', textAlign: 'left' },
    tr: { borderBottom: '1px solid #f1f5f9' },
    td: { padding: '16px 20px', fontSize: '14px', color: '#64748b' },
    tdBold: { padding: '16px 20px', fontSize: '14px', color: '#0f172a', fontWeight: '700' },
    emptyCell: { padding: '48px', textAlign: 'center', color: '#94a3b8' },
    btnAgendarSmall: { padding: '6px 14px', backgroundColor: '#eff6ff', color: '#2563eb', borderRadius: '8px', border: '1px solid #bfdbfe', cursor: 'pointer', fontWeight: '700', fontSize: '12px' },
    btnDeleteSmall: { padding: '6px 10px', backgroundColor: '#fee2e2', color: '#dc2626', borderRadius: '8px', border: '1px solid #fecaca', cursor: 'pointer', fontSize: '14px' },
};

export default ListaEspera;
