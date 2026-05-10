// ==============================================================================
// [SPRINT 2 - T026 / IA-01] Historia Clínica — Expediente + Evoluciones + IA
// Permite ver el expediente de un paciente, agregar notas de sesión con archivos
// adjuntos (multipart), y ejecutar análisis predictivo con Gemini.
// ==============================================================================
import React, { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import historiaService from '../services/historiaService';
import pacienteService from '../services/pacienteService';
import { useToast } from '../components/Toast';

const HistoriaClinica = () => {
    const { user } = useAuth();
    const { showToast, ToastContainer } = useToast();

    const [historias, setHistorias] = useState([]);
    const [pacientes, setPacientes] = useState([]);
    const [selectedHistoria, setSelectedHistoria] = useState(null);
    const [evoluciones, setEvoluciones] = useState([]);
    const [loading, setLoading] = useState(true);
    const [analizando, setAnalizando] = useState(null);
    const [busqueda, setBusqueda] = useState('');

    // Form para nueva evolución
    const [showForm, setShowForm] = useState(false);
    const [notasSesion, setNotasSesion] = useState('');
    const [archivo, setArchivo] = useState(null);

    const fetchData = useCallback(async () => {
        try {
            setLoading(true);
            const [historiasData, pacientesData, evolucionesData] = await Promise.all([
                historiaService.getHistorias(),
                pacienteService.getPacientes(),
                historiaService.getEvoluciones(),
            ]);
            setHistorias(Array.isArray(historiasData) ? historiasData : []);
            setPacientes(Array.isArray(pacientesData) ? pacientesData : []);
            setEvoluciones(Array.isArray(evolucionesData) ? evolucionesData : []);
        } catch (err) {
            showToast('Error cargando historias clínicas', 'error');
        } finally {
            setLoading(false);
        }
    }, [showToast]);

    useEffect(() => { fetchData(); }, [fetchData]);

    const getPacienteNombre = (historia) => {
        const pac = pacientes.find(p => p.id === historia.paciente);
        return pac ? pac.nombre : `Paciente #${historia.paciente}`;
    };

    const evolucionesDeHistoria = selectedHistoria
        ? evoluciones.filter(e => e.historia === selectedHistoria.id)
        : [];

    const handleCrearEvolucion = async (e) => {
        e.preventDefault();
        if (!selectedHistoria) return;
        try {
            await historiaService.crearEvolucion(
                { historia: selectedHistoria.id, notas_sesion: notasSesion },
                archivo
            );
            showToast('Nota de evolución registrada exitosamente', 'success');
            setNotasSesion('');
            setArchivo(null);
            setShowForm(false);
            fetchData();
        } catch (err) {
            showToast('Error al registrar la evolución', 'error');
        }
    };

    const handleAnalisisIA = async (evolucionId) => {
        setAnalizando(evolucionId);
        try {
            await historiaService.analizarConIA(evolucionId);
            showToast('Análisis de IA completado', 'success');
            fetchData();
        } catch (err) {
            const msg = err.response?.data?.error || 'Error al ejecutar análisis de IA';
            showToast(msg, 'error');
        } finally {
            setAnalizando(null);
        }
    };

    const historiasFiltradas = historias.filter(h => {
        if (!busqueda) return true;
        const nombre = getPacienteNombre(h).toLowerCase();
        return nombre.includes(busqueda.toLowerCase());
    });

    const formatFecha = (iso) => new Date(iso).toLocaleDateString('es-BO', {
        day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
    });

    return (
        <div style={styles.page}>
            <ToastContainer />

            <div style={styles.header}>
                <div>
                    <h1 style={styles.title}>🏥 Historia Clínica Digital</h1>
                    <p style={styles.subtitle}>T026 / IA-01 — Expedientes, evoluciones clínicas y diagnóstico predictivo con IA</p>
                </div>
            </div>

            <div style={styles.layout}>
                {/* Sidebar: Lista de pacientes con expediente */}
                <div style={styles.sidebar}>
                    <input
                        type="text"
                        placeholder="🔍 Buscar paciente..."
                        value={busqueda}
                        onChange={e => setBusqueda(e.target.value)}
                        style={styles.sidebarSearch}
                    />
                    <div style={styles.historiaList}>
                        {loading ? (
                            <p style={styles.emptyText}>Cargando expedientes...</p>
                        ) : historiasFiltradas.length === 0 ? (
                            <p style={styles.emptyText}>No hay expedientes.</p>
                        ) : (
                            historiasFiltradas.map(h => (
                                <div
                                    key={h.id}
                                    onClick={() => setSelectedHistoria(h)}
                                    style={{
                                        ...styles.historiaItem,
                                        ...(selectedHistoria?.id === h.id ? styles.historiaItemActive : {}),
                                    }}
                                >
                                    <div style={styles.historiaIcon}>📋</div>
                                    <div>
                                        <div style={styles.historiaNombre}>{getPacienteNombre(h)}</div>
                                        <div style={styles.historiaFecha}>
                                            Creado: {formatFecha(h.fecha_creacion)}
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Main: Detalle del expediente */}
                <div style={styles.mainContent}>
                    {!selectedHistoria ? (
                        <div style={styles.emptyState}>
                            <span style={{ fontSize: '64px' }}>📂</span>
                            <h3 style={{ color: '#475569', marginTop: '16px' }}>Selecciona un expediente</h3>
                            <p style={{ color: '#94a3b8' }}>Elige un paciente del panel izquierdo para ver su historia clínica.</p>
                        </div>
                    ) : (
                        <>
                            {/* Header del expediente */}
                            <div style={styles.expedienteHeader}>
                                <div>
                                    <h2 style={styles.expedienteTitulo}>
                                        📋 Expediente: {getPacienteNombre(selectedHistoria)}
                                    </h2>
                                    <p style={styles.expedienteSubtitulo}>
                                        ID: #{selectedHistoria.id} | Creado: {formatFecha(selectedHistoria.fecha_creacion)}
                                    </p>
                                </div>
                                <button
                                    onClick={() => setShowForm(!showForm)}
                                    style={styles.btnPrimary}
                                >
                                    {showForm ? 'Cerrar Formulario' : '+ Nueva Nota de Evolución'}
                                </button>
                            </div>

                            {/* Antecedentes */}
                            <div style={styles.antecedentesGrid}>
                                <div style={styles.antecedenteCard}>
                                    <h4 style={styles.antecedenteLabel}>Antecedentes Familiares</h4>
                                    <p style={styles.antecedenteText}>
                                        {selectedHistoria.antecedentes_familiares || 'Sin información registrada.'}
                                    </p>
                                </div>
                                <div style={styles.antecedenteCard}>
                                    <h4 style={styles.antecedenteLabel}>Antecedentes Personales</h4>
                                    <p style={styles.antecedenteText}>
                                        {selectedHistoria.antecedentes_personales || 'Sin información registrada.'}
                                    </p>
                                </div>
                                <div style={styles.antecedenteCard}>
                                    <h4 style={styles.antecedenteLabel}>Diagnóstico Preliminar</h4>
                                    <p style={styles.antecedenteText}>
                                        {selectedHistoria.diagnostico_preliminar || 'Pendiente de evaluación.'}
                                    </p>
                                </div>
                            </div>

                            {/* Form de nueva evolución */}
                            {showForm && (
                                <div style={styles.formCard}>
                                    <h3 style={styles.formTitle}>📝 Registrar Nota de Sesión</h3>
                                    <form onSubmit={handleCrearEvolucion}>
                                        <div style={styles.formGroup}>
                                            <label style={styles.label}>Notas de la Sesión *</label>
                                            <textarea
                                                value={notasSesion}
                                                onChange={e => setNotasSesion(e.target.value)}
                                                placeholder="Describa las observaciones clínicas de la sesión..."
                                                style={styles.textarea}
                                                required
                                            />
                                        </div>
                                        <div style={styles.formGroup}>
                                            <label style={styles.label}>Archivo Adjunto (Opcional)</label>
                                            <input
                                                type="file"
                                                onChange={e => setArchivo(e.target.files[0])}
                                                style={styles.fileInput}
                                            />
                                            <small style={styles.helpText}>
                                                ⚠️ El archivo se enviará como multipart/form-data
                                            </small>
                                        </div>
                                        <button type="submit" style={styles.btnPrimary}>
                                            Guardar Evolución
                                        </button>
                                    </form>
                                </div>
                            )}

                            {/* Timeline de evoluciones */}
                            <h3 style={styles.sectionTitle}>
                                🕐 Evoluciones Clínicas ({evolucionesDeHistoria.length})
                            </h3>

                            {evolucionesDeHistoria.length === 0 ? (
                                <div style={styles.emptyTimeline}>
                                    No hay notas de evolución registradas para este paciente.
                                </div>
                            ) : (
                                <div style={styles.timeline}>
                                    {evolucionesDeHistoria.map(evo => (
                                        <div key={evo.id} style={styles.timelineItem}>
                                            <div style={styles.timelineDot} />
                                            <div style={styles.timelineCard}>
                                                <div style={styles.timelineHeader}>
                                                    <span style={styles.timelineFecha}>
                                                        📅 {formatFecha(evo.fecha_sesion)}
                                                    </span>
                                                    {evo.archivo_adjunto && (
                                                        <a
                                                            href={evo.archivo_adjunto}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            style={styles.attachLink}
                                                        >
                                                            📎 Ver adjunto
                                                        </a>
                                                    )}
                                                </div>
                                                <p style={styles.timelineNotas}>{evo.notas_sesion}</p>

                                                {/* Bloque de IA */}
                                                {evo.analisis_ia ? (
                                                    <div style={styles.iaCard}>
                                                        <div style={styles.iaHeader}>
                                                            <span>🤖 Análisis Predictivo de IA (Gemini)</span>
                                                        </div>
                                                        <p style={styles.iaText}>{evo.analisis_ia}</p>
                                                    </div>
                                                ) : (
                                                    <button
                                                        onClick={() => handleAnalisisIA(evo.id)}
                                                        disabled={analizando === evo.id}
                                                        style={{
                                                            ...styles.btnIA,
                                                            opacity: analizando === evo.id ? 0.6 : 1,
                                                        }}
                                                    >
                                                        {analizando === evo.id
                                                            ? '⏳ Analizando con Gemini...'
                                                            : '🤖 Analizar con IA'}
                                                    </button>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};

// ==============================================================================
// ESTILOS
// ==============================================================================
const styles = {
    page: { padding: 'clamp(16px, 5vw, 40px)', backgroundColor: '#f1f5f9', minHeight: '100vh', fontFamily: '"Inter", sans-serif' },
    header: { marginBottom: '24px' },
    title: { fontSize: '28px', fontWeight: '800', color: '#0f172a', margin: 0 },
    subtitle: { fontSize: '14px', color: '#64748b', marginTop: '4px' },
    layout: { display: 'flex', gap: '24px', minHeight: 'calc(100vh - 160px)' },
    sidebar: { width: '320px', flexShrink: 0 },
    sidebarSearch: { width: '100%', padding: '12px 16px', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '14px', marginBottom: '16px', outline: 'none', boxSizing: 'border-box', backgroundColor: 'white' },
    historiaList: { display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: 'calc(100vh - 260px)', overflowY: 'auto' },
    historiaItem: { display: 'flex', alignItems: 'center', gap: '12px', padding: '14px 16px', borderRadius: '14px', backgroundColor: 'white', border: '1px solid #e2e8f0', cursor: 'pointer', transition: 'all 0.2s' },
    historiaItemActive: { backgroundColor: '#eff6ff', borderColor: '#3b82f6', boxShadow: '0 0 0 2px rgba(59,130,246,0.2)' },
    historiaIcon: { fontSize: '24px' },
    historiaNombre: { fontSize: '14px', fontWeight: '700', color: '#0f172a' },
    historiaFecha: { fontSize: '12px', color: '#94a3b8' },
    emptyText: { textAlign: 'center', color: '#94a3b8', padding: '32px', fontSize: '14px' },
    mainContent: { flex: 1, minWidth: 0 },
    emptyState: { display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '60vh', backgroundColor: 'white', borderRadius: '20px', border: '1px solid #e2e8f0' },
    expedienteHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', padding: '24px', backgroundColor: 'white', borderRadius: '16px', border: '1px solid #e2e8f0' },
    expedienteTitulo: { fontSize: '20px', fontWeight: '800', color: '#0f172a', margin: 0 },
    expedienteSubtitulo: { fontSize: '13px', color: '#94a3b8', marginTop: '4px' },
    antecedentesGrid: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' },
    antecedenteCard: { backgroundColor: 'white', padding: '20px', borderRadius: '16px', border: '1px solid #e2e8f0' },
    antecedenteLabel: { fontSize: '12px', fontWeight: '700', color: '#64748b', textTransform: 'uppercase', marginBottom: '8px', letterSpacing: '0.5px' },
    antecedenteText: { fontSize: '14px', color: '#475569', lineHeight: '1.6' },
    formCard: { backgroundColor: 'white', padding: '28px', borderRadius: '16px', border: '1px solid #e2e8f0', marginBottom: '24px' },
    formTitle: { fontSize: '18px', fontWeight: '700', color: '#0f172a', marginBottom: '20px' },
    formGroup: { marginBottom: '16px' },
    label: { display: 'block', fontSize: '12px', fontWeight: '700', color: '#64748b', marginBottom: '8px', textTransform: 'uppercase' },
    textarea: { width: '100%', padding: '12px 16px', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '14px', minHeight: '120px', resize: 'vertical', outline: 'none', boxSizing: 'border-box', fontFamily: 'inherit', lineHeight: '1.6' },
    fileInput: { width: '100%', padding: '10px', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '14px' },
    helpText: { fontSize: '12px', color: '#94a3b8', marginTop: '4px', display: 'block' },
    btnPrimary: { backgroundColor: '#2563eb', color: 'white', padding: '12px 24px', borderRadius: '12px', border: 'none', fontWeight: '700', fontSize: '14px', cursor: 'pointer', boxShadow: '0 4px 12px rgba(37,99,235,0.3)' },
    sectionTitle: { fontSize: '18px', fontWeight: '700', color: '#0f172a', marginBottom: '16px' },
    emptyTimeline: { textAlign: 'center', padding: '40px', backgroundColor: 'white', borderRadius: '16px', border: '1px solid #e2e8f0', color: '#94a3b8' },
    timeline: { display: 'flex', flexDirection: 'column', gap: '16px' },
    timelineItem: { display: 'flex', gap: '16px', position: 'relative' },
    timelineDot: { width: '14px', height: '14px', borderRadius: '50%', backgroundColor: '#3b82f6', flexShrink: 0, marginTop: '6px', boxShadow: '0 0 0 4px rgba(59,130,246,0.15)' },
    timelineCard: { flex: 1, backgroundColor: 'white', padding: '24px', borderRadius: '16px', border: '1px solid #e2e8f0' },
    timelineHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' },
    timelineFecha: { fontSize: '13px', fontWeight: '600', color: '#64748b' },
    attachLink: { fontSize: '13px', color: '#3b82f6', textDecoration: 'none', fontWeight: '600' },
    timelineNotas: { fontSize: '14px', color: '#475569', lineHeight: '1.8', whiteSpace: 'pre-wrap' },
    iaCard: { marginTop: '16px', padding: '20px', borderRadius: '14px', background: 'linear-gradient(135deg, #f0f9ff 0%, #ede9fe 100%)', border: '1px solid #c7d2fe' },
    iaHeader: { fontSize: '13px', fontWeight: '700', color: '#4f46e5', marginBottom: '8px' },
    iaText: { fontSize: '14px', color: '#475569', lineHeight: '1.8', whiteSpace: 'pre-wrap' },
    btnIA: { marginTop: '12px', padding: '10px 20px', borderRadius: '10px', border: '1px solid #c7d2fe', backgroundColor: '#eef2ff', color: '#4f46e5', fontWeight: '700', fontSize: '13px', cursor: 'pointer', transition: 'all 0.2s' },
};

export default HistoriaClinica;
