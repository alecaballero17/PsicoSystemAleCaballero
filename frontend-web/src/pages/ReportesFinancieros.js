// ==============================================================================
// [RF-27 EXTENDIDO] Reportes Híbridos — Manual + Voice-to-Report IA
// Filtros reales: Fecha, Estado de Cita, Top Psicólogo, Monto
// ==============================================================================
import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { useToast } from '../components/Toast';

const API_BASE = process.env.REACT_APP_API_URL || 'https://psicosystem-si2.onrender.com';

// ─── Colores de estado ────────────────────────────────────────────────────────
const ESTADO_COLORS = {
  PENDIENTE:   { bg: '#fef9c3', text: '#854d0e', border: '#fde047' },
  COMPLETADA:  { bg: '#dcfce7', text: '#166534', border: '#86efac' },
  CANCELADA:   { bg: '#fee2e2', text: '#991b1b', border: '#fca5a5' },
  NO_ASISTIO:  { bg: '#f3e8ff', text: '#6b21a8', border: '#d8b4fe' },
};

const ESTADO_LABELS = {
  PENDIENTE: 'Pendiente',
  COMPLETADA: 'Completada',
  CANCELADA: 'Cancelada',
  NO_ASISTIO: 'No Asistió',
};

// ─── Helpers ─────────────────────────────────────────────────────────────────
function getToken() {
  try { return JSON.parse(localStorage.getItem('psico_user'))?.access || ''; }
  catch { return ''; }
}

function authHeaders() {
  return { headers: { Authorization: `Bearer ${getToken()}` } };
}

function downloadBlob(base64, filename) {
  const byteChars = atob(base64);
  const byteArr = new Uint8Array(byteChars.length);
  for (let i = 0; i < byteChars.length; i++) byteArr[i] = byteChars.charCodeAt(i);
  const blob = new Blob([byteArr], { type: 'application/pdf' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

function formatFiltroChip(key, value) {
  if (!value && value !== 0) return null;
  const map = {
    fecha_inicio: { icon: '📅', label: `Desde: ${value}` },
    fecha_fin:    { icon: '📅', label: `Hasta: ${value}` },
    estado_cita:  { icon: '🚦', label: ESTADO_LABELS[value] || value },
    top_psicologo:{ icon: '👨‍⚕️', label: 'Top Psicólogo' },
    monto_min:    { icon: '💰', label: `Monto ≥ ${value} BOB` },
    monto_max:    { icon: '💰', label: `Monto ≤ ${value} BOB` },
  };
  return map[key] || null;
}

// ─── Componente Principal ─────────────────────────────────────────────────────
export default function ReportesFinancieros() {
  const { showToast, ToastContainer } = useToast();

  // ── Estado tabla manual
  const [citas, setCitas]           = useState([]);
  const [loadingTabla, setLoadingTabla] = useState(false);
  const [busqueda, setBusqueda]     = useState('');
  const [filtroFechaInicio, setFiltroFechaInicio] = useState('');
  const [filtroFechaFin, setFiltroFechaFin]       = useState('');
  const [filtroEstado, setFiltroEstado]             = useState('');

  // ── Estado Voice-to-Report
  const [micState, setMicState]         = useState('idle'); // idle | recording | processing
  const [transcript, setTranscript]     = useState('');
  const [filtrosIA, setFiltrosIA]       = useState(null);
  const [resumenIA, setResumenIA]       = useState(null);
  const [pdfBase64, setPdfBase64]       = useState(null);

  const recognitionRef = useRef(null);

  // ── Cargar tabla de citas
  const cargarCitas = useCallback(async () => {
    setLoadingTabla(true);
    try {
      const params = new URLSearchParams();
      if (filtroFechaInicio) params.append('fecha_inicio', filtroFechaInicio);
      if (filtroFechaFin)    params.append('fecha_fin', filtroFechaFin);
      if (filtroEstado)      params.append('estado', filtroEstado);
      const res = await axios.get(
        `${API_BASE}/api/reportes/citas/?${params.toString()}`,
        authHeaders()
      );
      setCitas(res.data.citas || []);
    } catch (err) {
      showToast('Error al cargar las citas', 'error');
    } finally {
      setLoadingTabla(false);
    }
  }, [filtroFechaInicio, filtroFechaFin, filtroEstado]);

  useEffect(() => { cargarCitas(); }, [cargarCitas]);

  // ── Filtro client-side (búsqueda de texto)
  const citasFiltradas = citas.filter(c =>
    `${c.paciente} ${c.psicologo} ${c.motivo}`.toLowerCase().includes(busqueda.toLowerCase())
  );

  // ── Exportar Excel (descarga la tabla actual)
  const exportarExcel = async () => {
    try {
      const params = new URLSearchParams();
      if (filtroFechaInicio) params.append('fecha_inicio', filtroFechaInicio);
      if (filtroFechaFin)    params.append('fecha_fin', filtroFechaFin);
      if (filtroEstado)      params.append('estado', filtroEstado);
      params.append('formato', 'excel');
      showToast('Generando Excel...', 'info');
      // Generación client-side con los datos ya cargados
      const rows = [['#','Paciente','Psicólogo','Fecha/Hora','Estado','Motivo']];
      citasFiltradas.forEach((c,i) => rows.push([i+1,c.paciente,c.psicologo,c.fecha_hora,c.estado,c.motivo]));
      const csvContent = rows.map(r => r.join(',')).join('\n');
      const blob = new Blob(['\uFEFF'+csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = `reporte_citas_${new Date().toISOString().slice(0,10)}.csv`; a.click();
      URL.revokeObjectURL(url);
      showToast(`Excel descargado — ${citasFiltradas.length} registros`, 'success');
    } catch (err) {
      showToast('Error al exportar', 'error');
    }
  };

  // ── Mic: iniciar grabación
  const iniciarMic = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      showToast('Tu navegador no soporta voz. Usa Chrome.', 'warning');
      return;
    }
    const rec = new SpeechRecognition();
    rec.lang = 'es-ES';
    rec.interimResults = true;
    rec.continuous = true;
    rec.onresult = (e) => {
      const t = Array.from(e.results).map(r => r[0].transcript).join('');
      setTranscript(t);
    };
    rec.onerror = () => { showToast('Error de micrófono', 'error'); setMicState('idle'); };
    rec.start();
    recognitionRef.current = rec;
    setMicState('recording');
    setFiltrosIA(null);
    setResumenIA(null);
    setPdfBase64(null);
  };

  // ── Mic: detener y enviar a IA
  const detenerMic = async () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    if (!transcript.trim()) { setMicState('idle'); return; }
    setMicState('processing');
    try {
      const res = await axios.post(
        `${API_BASE}/api/reportes/voz/`,
        { transcript },
        authHeaders()
      );
      setFiltrosIA(res.data.filtros_interpretados);
      setResumenIA(res.data.resumen);
      setPdfBase64(res.data.pdf_base64);
      // Descarga automática del PDF
      const fecha = new Date().toISOString().slice(0,10);
      downloadBlob(res.data.pdf_base64, `reporte_voz_ia_${fecha}.pdf`);
      showToast(`✅ PDF generado — ${res.data.resumen.total_citas} citas encontradas`, 'success');
    } catch (err) {
      const msg = err.response?.data?.error || 'Error al procesar el comando de voz';
      showToast(msg, 'error');
    } finally {
      setMicState('idle');
    }
  };

  // ── Renderizado
  return (
    <div style={s.page}>
      <ToastContainer />

      {/* ── HEADER */}
      <div style={s.header}>
        <div>
          <h1 style={s.title}>📊 Reportes &amp; Auditoría</h1>
          <p style={s.subtitle}>RF-27 — Historial de citas, filtros manuales y Voice-to-Report con IA</p>
        </div>
      </div>

      {/* ══════════════════════════════════════════════════════════
          SECCIÓN 1: VOICE-TO-REPORT IA
      ══════════════════════════════════════════════════════════ */}
      <div style={s.card}>
        <div style={s.cardHeader}>
          <span style={s.cardIcon}>🎤</span>
          <div>
            <h2 style={s.cardTitle}>Voice-to-Report con IA</h2>
            <p style={s.cardDesc}>Mantén presionado el micrófono y dicta un comando. Gemini interpretará los filtros y generará el PDF automáticamente.</p>
          </div>
        </div>

        {/* Barra de transcript */}
        <div style={s.voiceBar}>
          <input
            style={s.transcriptInput}
            value={transcript}
            onChange={e => setTranscript(e.target.value)}
            placeholder='Ej: "Citas canceladas de enero a marzo" o "Psicólogo con más citas este mes"'
            disabled={micState === 'processing'}
          />
          {/* Botón micrófono */}
          <button
            id="btn-mic-voice"
            style={{
              ...s.micBtn,
              ...(micState === 'recording' ? s.micBtnRecording : {}),
              ...(micState === 'processing' ? s.micBtnProcessing : {}),
            }}
            onMouseDown={micState === 'idle' ? iniciarMic : undefined}
            onMouseUp={micState === 'recording' ? detenerMic : undefined}
            onTouchStart={micState === 'idle' ? iniciarMic : undefined}
            onTouchEnd={micState === 'recording' ? detenerMic : undefined}
            disabled={micState === 'processing'}
            title={micState === 'idle' ? 'Mantén presionado para grabar' : ''}
          >
            {micState === 'idle'       && '🎤'}
            {micState === 'recording'  && '⏹'}
            {micState === 'processing' && <span style={s.spinner} />}
          </button>

          {/* También se puede enviar texto escrito directamente */}
          {micState === 'idle' && transcript && (
            <button id="btn-send-transcript" style={s.sendBtn} onClick={detenerMic}>
              Analizar →
            </button>
          )}
        </div>

        {/* Label de estado del micrófono */}
        <div style={s.micStatus}>
          {micState === 'idle'       && <span style={s.statusIdle}>Presiona y mantén 🎤 para grabar, o escribe tu comando arriba</span>}
          {micState === 'recording'  && <span style={s.statusRecording}>🔴 Escuchando... Suelta el botón cuando termines</span>}
          {micState === 'processing' && <span style={s.statusProcessing}>⚡ Analizando con Gemini IA y generando PDF...</span>}
        </div>

        {/* Chips de filtros interpretados */}
        {filtrosIA && (
          <div style={s.chipsSection}>
            <span style={s.chipsLabel}>Filtros interpretados por IA:</span>
            <div style={s.chipsRow}>
              {Object.entries(filtrosIA).map(([k, v]) => {
                const chip = formatFiltroChip(k, v);
                if (!chip || v === null || v === false) return null;
                return (
                  <span key={k} style={s.chip}>
                    {chip.icon} {chip.label}
                  </span>
                );
              })}
            </div>
          </div>
        )}

        {/* Resumen IA */}
        {resumenIA && (
          <div style={s.resumenGrid}>
            <div style={s.resumenCard}>
              <span style={s.resumenNum}>{resumenIA.total_citas}</span>
              <span style={s.resumenLbl}>Citas encontradas</span>
            </div>
            <div style={s.resumenCard}>
              <span style={s.resumenNum}>{parseFloat(resumenIA.total_recaudado_bobs || 0).toFixed(2)}</span>
              <span style={s.resumenLbl}>BOB Recaudados</span>
            </div>
            {resumenIA.top_psicologo && (
              <div style={{ ...s.resumenCard, gridColumn: 'span 2' }}>
                <span style={s.resumenNum}>👨‍⚕️ {resumenIA.top_psicologo.nombre}</span>
                <span style={s.resumenLbl}>Psicólogo más activo — {resumenIA.top_psicologo.total_citas} citas</span>
              </div>
            )}
          </div>
        )}

        {/* Botón re-descargar PDF */}
        {pdfBase64 && (
          <button
            id="btn-redownload-pdf"
            style={s.btnRedownload}
            onClick={() => downloadBlob(pdfBase64, `reporte_voz_ia_${new Date().toISOString().slice(0,10)}.pdf`)}
          >
            ⬇️ Volver a descargar PDF
          </button>
        )}
      </div>

      {/* ══════════════════════════════════════════════════════════
          SECCIÓN 2: TABLA DE CITAS (Filtros manuales)
      ══════════════════════════════════════════════════════════ */}
      <div style={s.card}>
        <div style={s.cardHeader}>
          <span style={s.cardIcon}>📋</span>
          <div>
            <h2 style={s.cardTitle}>Historial de Citas</h2>
            <p style={s.cardDesc}>Filtros manuales por fecha y estado. Exporta a PDF o CSV.</p>
          </div>
        </div>

        {/* Controles */}
        <div style={s.controlsRow}>
          <input
            id="busqueda-citas"
            style={s.searchInput}
            placeholder="🔍 Buscar paciente, psicólogo o motivo..."
            value={busqueda}
            onChange={e => setBusqueda(e.target.value)}
          />
          <input type="date" style={s.dateInput} value={filtroFechaInicio}
            onChange={e => setFiltroFechaInicio(e.target.value)}
            title="Fecha inicio" />
          <input type="date" style={s.dateInput} value={filtroFechaFin}
            onChange={e => setFiltroFechaFin(e.target.value)}
            title="Fecha fin" />
          <select id="filtro-estado" style={s.selectInput} value={filtroEstado}
            onChange={e => setFiltroEstado(e.target.value)}>
            <option value="">Todos los estados</option>
            <option value="PENDIENTE">Pendiente</option>
            <option value="COMPLETADA">Completada</option>
            <option value="CANCELADA">Cancelada</option>
            <option value="NO_ASISTIO">No Asistió</option>
          </select>
          <button id="btn-exportar-csv" style={s.btnExport} onClick={exportarExcel}>
            📥 CSV
          </button>
        </div>

        {/* Tabla */}
        <div style={s.tableWrapper}>
          {loadingTabla ? (
            <div style={s.emptyState}>⏳ Cargando citas...</div>
          ) : citasFiltradas.length === 0 ? (
            <div style={s.emptyState}>Sin resultados con los filtros actuales.</div>
          ) : (
            <table style={s.table}>
              <thead>
                <tr>
                  {['#','Paciente','Psicólogo','Fecha/Hora','Estado','Motivo'].map(h => (
                    <th key={h} style={s.th}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {citasFiltradas.map((c, i) => {
                  const ec = ESTADO_COLORS[c.estado] || {};
                  return (
                    <tr key={c.id} style={i % 2 === 0 ? s.trEven : s.trOdd}>
                      <td style={s.td}>{i + 1}</td>
                      <td style={{ ...s.td, fontWeight: 600 }}>{c.paciente}</td>
                      <td style={s.td}>{c.psicologo}</td>
                      <td style={s.td}>{c.fecha_hora}</td>
                      <td style={s.td}>
                        <span style={{
                          padding: '3px 10px', borderRadius: '999px', fontSize: '12px',
                          fontWeight: 700, backgroundColor: ec.bg, color: ec.text,
                          border: `1px solid ${ec.border}`,
                        }}>
                          {ESTADO_LABELS[c.estado] || c.estado}
                        </span>
                      </td>
                      <td style={{ ...s.td, color: '#64748b', fontSize: '13px' }}>{c.motivo || '—'}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
        <div style={s.tableFooter}>
          Mostrando <b>{citasFiltradas.length}</b> de <b>{citas.length}</b> citas
        </div>
      </div>
    </div>
  );
}

// ─── Estilos ─────────────────────────────────────────────────────────────────
const s = {
  page:        { padding: '32px 40px', background: 'linear-gradient(135deg,#f0f4ff 0%,#f8fafc 100%)', minHeight: '100vh', fontFamily: '"Inter",sans-serif' },
  header:      { marginBottom: '28px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  title:       { fontSize: '28px', fontWeight: 800, color: '#0f172a', margin: 0 },
  subtitle:    { fontSize: '14px', color: '#64748b', marginTop: '4px' },

  card:        { background: 'white', borderRadius: '20px', border: '1px solid #e2e8f0', padding: '28px', marginBottom: '24px', boxShadow: '0 4px 24px rgba(0,0,0,0.06)' },
  cardHeader:  { display: 'flex', gap: '16px', alignItems: 'flex-start', marginBottom: '24px' },
  cardIcon:    { fontSize: '32px', lineHeight: 1 },
  cardTitle:   { fontSize: '18px', fontWeight: 800, color: '#0f172a', margin: 0 },
  cardDesc:    { fontSize: '13px', color: '#64748b', marginTop: '4px' },

  // Voice bar
  voiceBar:    { display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '12px' },
  transcriptInput: {
    flex: 1, padding: '14px 18px', borderRadius: '14px',
    border: '2px solid #e2e8f0', fontSize: '14px', outline: 'none',
    transition: 'border-color .2s', background: '#f8fafc',
  },
  micBtn: {
    width: '52px', height: '52px', borderRadius: '50%', border: 'none',
    background: 'linear-gradient(135deg,#2563eb,#7c3aed)', color: 'white',
    fontSize: '22px', cursor: 'pointer', display: 'flex', alignItems: 'center',
    justifyContent: 'center', flexShrink: 0,
    boxShadow: '0 4px 14px rgba(37,99,235,0.35)', transition: 'all .2s',
    userSelect: 'none',
  },
  micBtnRecording: {
    background: 'linear-gradient(135deg,#dc2626,#b91c1c)',
    boxShadow: '0 0 0 6px rgba(220,38,38,0.25)',
    animation: 'pulse 1.2s ease-in-out infinite',
  },
  micBtnProcessing: {
    background: 'linear-gradient(135deg,#0ea5e9,#2563eb)',
    cursor: 'not-allowed', opacity: 0.8,
  },
  sendBtn: {
    padding: '14px 22px', borderRadius: '14px', border: 'none',
    background: 'linear-gradient(135deg,#2563eb,#7c3aed)', color: 'white',
    fontWeight: 700, fontSize: '14px', cursor: 'pointer', whiteSpace: 'nowrap',
  },
  micStatus:   { marginBottom: '16px', minHeight: '20px' },
  statusIdle:       { fontSize: '13px', color: '#94a3b8' },
  statusRecording:  { fontSize: '13px', color: '#dc2626', fontWeight: 600 },
  statusProcessing: { fontSize: '13px', color: '#2563eb', fontWeight: 600 },
  spinner: {
    display: 'inline-block', width: '22px', height: '22px',
    border: '3px solid rgba(255,255,255,0.3)', borderTopColor: 'white',
    borderRadius: '50%', animation: 'spin 0.8s linear infinite',
  },

  // Chips
  chipsSection: { marginBottom: '16px' },
  chipsLabel:   { fontSize: '12px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: '8px', display: 'block' },
  chipsRow:     { display: 'flex', flexWrap: 'wrap', gap: '8px' },
  chip: {
    padding: '6px 14px', borderRadius: '999px', background: '#eff6ff',
    color: '#1d4ed8', border: '1px solid #bfdbfe', fontSize: '13px', fontWeight: 600,
  },

  // Resumen IA
  resumenGrid:  { display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(160px,1fr))', gap: '16px', marginBottom: '20px' },
  resumenCard:  { background: '#f8fafc', borderRadius: '14px', padding: '20px', border: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' },
  resumenNum:   { fontSize: '24px', fontWeight: 800, color: '#0f172a' },
  resumenLbl:   { fontSize: '12px', color: '#64748b', textAlign: 'center' },

  btnRedownload: {
    padding: '10px 20px', borderRadius: '12px', border: '2px solid #2563eb',
    background: 'white', color: '#2563eb', fontWeight: 700, fontSize: '14px',
    cursor: 'pointer',
  },

  // Tabla
  controlsRow:  { display: 'flex', gap: '12px', flexWrap: 'wrap', marginBottom: '20px', alignItems: 'center' },
  searchInput:  { flex: 1, minWidth: '220px', padding: '11px 16px', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '14px', outline: 'none' },
  dateInput:    { padding: '11px 14px', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '14px', outline: 'none' },
  selectInput:  { padding: '11px 14px', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '14px', outline: 'none', background: 'white' },
  btnExport:    { padding: '11px 20px', borderRadius: '12px', border: 'none', background: '#10b981', color: 'white', fontWeight: 700, fontSize: '14px', cursor: 'pointer' },

  tableWrapper: { overflowX: 'auto', borderRadius: '12px', border: '1px solid #e2e8f0' },
  table:        { width: '100%', borderCollapse: 'collapse', fontSize: '14px' },
  th:           { padding: '13px 16px', textAlign: 'left', background: '#1e3a8a', color: 'white', fontWeight: 700, fontSize: '12px', textTransform: 'uppercase', whiteSpace: 'nowrap' },
  trEven:       { background: 'white' },
  trOdd:        { background: '#f8fafc' },
  td:           { padding: '12px 16px', borderBottom: '1px solid #f1f5f9', color: '#334155', whiteSpace: 'nowrap' },
  emptyState:   { padding: '60px', textAlign: 'center', color: '#94a3b8', fontSize: '15px' },
  tableFooter:  { padding: '14px 0 0', fontSize: '13px', color: '#64748b', textAlign: 'right' },
};
