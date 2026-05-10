// ==============================================================================
// [SPRINT 2 - RF-27] Reportes Financieros e Historial de Citas Híbrido (Manual + IA)
// Integración con Voice-to-Report (Voz a SQL) usando Gemini y Web Speech API.
// ==============================================================================
import React, { useState, useEffect, useRef } from 'react';
import finanzaService from '../services/finanzaService';
import { useToast } from '../components/Toast';

const ReportesFinancieros = () => {
    const { showToast, ToastContainer } = useToast();

    // Estado para Voice-to-Report
    const [isRecording, setIsRecording] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [filtrosIA, setFiltrosIA] = useState(null);

    // Estado para reporte manual (existente)
    const [fechaInicio, setFechaInicio] = useState('');
    const [fechaFin, setFechaFin] = useState('');
    const [generarAudio, setGenerarAudio] = useState(true);
    const [reporteManual, setReporteManual] = useState(null);
    const [loadingManual, setLoadingManual] = useState(false);

    // Ref para el reconocimiento de voz
    const recognitionRef = useRef(null);

    // ==========================================================
    // 🎤 Lógica de Voice-to-Report (Web Speech API)
    // ==========================================================
    useEffect(() => {
        // Inicializar Speech Recognition solo si el navegador lo soporta
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            recognitionRef.current = new SpeechRecognition();
            recognitionRef.current.continuous = false; // Solo una frase
            recognitionRef.current.interimResults = true; // Mostrar resultados parciales
            recognitionRef.current.lang = 'es-ES';

            recognitionRef.current.onstart = () => {
                setIsRecording(true);
                setTranscript('');
                setFiltrosIA(null); // Limpiar filtros previos
            };

            recognitionRef.current.onresult = (event) => {
                let currentTranscript = '';
                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    currentTranscript += event.results[i][0].transcript;
                }
                setTranscript(currentTranscript);
            };

            recognitionRef.current.onerror = (event) => {
                setIsRecording(false);
                if (event.error !== 'no-speech') {
                    showToast(`Error de micrófono: ${event.error}`, 'error');
                }
            };

            recognitionRef.current.onend = () => {
                setIsRecording(false);
                // Si hay texto al terminar de grabar, se envía al backend
            };
        } else {
            console.warn("Speech Recognition no está soportado en este navegador.");
        }
    }, []);

    // Efecto para enviar el texto al backend cuando se termina de grabar
    useEffect(() => {
        const procesarVozConIA = async () => {
            if (!isRecording && transcript && !isProcessing && !filtrosIA) {
                setIsProcessing(true);
                try {
                    // Enviar al Backend -> Gemini -> PDF
                    const data = await finanzaService.generarReporteVoz(transcript);
                    
                    // Mostrar los filtros aplicados
                    setFiltrosIA(data.filtros);
                    showToast('Reporte generado automáticamente', 'success');

                    // Descargar PDF usando la respuesta base64
                    const linkSource = `data:application/pdf;base64,${data.pdf_base64}`;
                    const downloadLink = document.createElement("a");
                    const fileName = `Reporte_IA_${new Date().getTime()}.pdf`;
                    downloadLink.href = linkSource;
                    downloadLink.download = fileName;
                    downloadLink.click();

                } catch (error) {
                    showToast('Error al interpretar el comando de voz', 'error');
                    console.error(error);
                } finally {
                    setIsProcessing(false);
                }
            }
        };

        procesarVozConIA();
    }, [isRecording, transcript]);

    const startRecording = () => {
        if (recognitionRef.current && !isProcessing) {
            recognitionRef.current.start();
        } else if (!recognitionRef.current) {
            showToast('Su navegador no soporta búsqueda por voz.', 'error');
        }
    };

    const stopRecording = () => {
        if (recognitionRef.current) {
            recognitionRef.current.stop();
        }
    };

    // ==========================================================
    // 📊 Lógica de Reporte Manual (Existente extendido)
    // ==========================================================
    const handleGenerarReporteManual = async (e) => {
        e.preventDefault();
        if (!fechaInicio || !fechaFin) {
            showToast('Debe seleccionar ambas fechas', 'warning');
            return;
        }
        try {
            setLoadingManual(true);
            const data = await finanzaService.generarReporte(fechaInicio, fechaFin, generarAudio);
            setReporteManual(data);
            showToast('Reporte generado exitosamente', 'success');
        } catch (err) {
            const msg = err.response?.data?.error || 'Error al generar el reporte';
            showToast(msg, 'error');
        } finally {
            setLoadingManual(false);
        }
    };

    return (
        <div style={styles.page}>
            <ToastContainer />

            <div style={styles.header}>
                <h1 style={styles.title}>🤖 Reportes e Inteligencia Artificial</h1>
                <p style={styles.subtitle}>Auditoría, filtros inteligentes y voz a consulta (Voice-to-SQL)</p>
            </div>

            {/* SECCIÓN 1: Voice-to-Report (IA) */}
            <div style={{...styles.card, marginBottom: '32px'}}>
                <h3 style={styles.sectionTitle}>🎙️ Asistente de Reportes con IA (Gemini)</h3>
                <p style={{fontSize: '14px', color: '#64748b', marginBottom: '20px'}}>
                    Mantén presionado el micrófono y dicta qué información necesitas extraer del sistema. 
                    Por ejemplo: <em>"Generar reporte de las citas canceladas este mes"</em> o <em>"Pagos mayores a 100 bolivianos"</em>.
                </p>

                <div style={styles.voiceContainer}>
                    <button 
                        onMouseDown={startRecording}
                        onMouseUp={stopRecording}
                        onMouseLeave={stopRecording}
                        onTouchStart={startRecording}
                        onTouchEnd={stopRecording}
                        style={{
                            ...styles.micButton,
                            backgroundColor: isRecording ? '#ef4444' : (isProcessing ? '#eab308' : '#3b82f6'),
                            animation: isRecording ? 'pulse 1.5s infinite' : 'none'
                        }}
                        disabled={isProcessing}
                    >
                        {isRecording ? '🎤' : (isProcessing ? '⏳' : '🎙️')}
                    </button>
                    
                    <div style={styles.transcriptBox}>
                        {isRecording ? (
                            <span style={{color: '#ef4444', fontWeight: '600'}}>Escuchando... {transcript}</span>
                        ) : isProcessing ? (
                            <span style={{color: '#eab308', fontWeight: '600'}}>🧠 Analizando filtros con IA y generando PDF...</span>
                        ) : transcript ? (
                            <span style={{color: '#0f172a'}}>"{transcript}"</span>
                        ) : (
                            <span style={{color: '#94a3b8'}}>El texto dictado aparecerá aquí...</span>
                        )}
                    </div>
                </div>

                {/* Confirmación visual de filtros aplicados */}
                {filtrosIA && (
                    <div style={styles.filtrosBox}>
                        <h4 style={{fontSize: '13px', margin: '0 0 10px 0', color: '#475569'}}>Filtros interpretados por Gemini:</h4>
                        <div style={{display: 'flex', gap: '8px', flexWrap: 'wrap'}}>
                            {filtrosIA.fecha_inicio && <span style={styles.chip}>📅 Desde: {filtrosIA.fecha_inicio}</span>}
                            {filtrosIA.fecha_fin && <span style={styles.chip}>📅 Hasta: {filtrosIA.fecha_fin}</span>}
                            {filtrosIA.estado_cita && <span style={styles.chip}>🚦 Estado: {filtrosIA.estado_cita}</span>}
                            {filtrosIA.monto_min && <span style={styles.chip}>💰 Min: {filtrosIA.monto_min} BOB</span>}
                            {filtrosIA.monto_max && <span style={styles.chip}>💰 Max: {filtrosIA.monto_max} BOB</span>}
                            {filtrosIA.top_psicologo && <span style={styles.chip}>👨‍⚕️ Top Psicólogo</span>}
                            {Object.values(filtrosIA).every(v => v === null || v === false) && (
                                <span style={{fontSize: '13px', color: '#ef4444'}}>No se detectaron filtros en el audio. Se consultó toda la base de datos.</span>
                            )}
                        </div>
                        <p style={{fontSize: '12px', color: '#10b981', marginTop: '12px', fontWeight: '700'}}>✅ PDF Descargado automáticamente.</p>
                    </div>
                )}
            </div>

            {/* SECCIÓN 2: Reporte Manual y Ejecutivo */}
            <div style={styles.card}>
                <h3 style={styles.sectionTitle}>🗓️ Reporte Ejecutivo Manual</h3>
                <form onSubmit={handleGenerarReporteManual} style={styles.formRow}>
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
                                Generar lectura (MP3)
                            </label>
                        </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'flex-end' }}>
                        <button type="submit" style={styles.btnPrimary} disabled={loadingManual}>
                            {loadingManual ? '⏳ Generando...' : '📊 Obtener Resumen'}
                        </button>
                    </div>
                </form>

                {reporteManual && (
                    <div style={styles.reporteContainer}>
                        <div style={{display: 'flex', justifyContent: 'space-between'}}>
                            <h4 style={{margin: '0 0 10px 0'}}>Resultado del Análisis</h4>
                            <span style={{fontSize: '12px', color: '#64748b'}}>{reporteManual.fecha_inicio} al {reporteManual.fecha_fin}</span>
                        </div>
                        <div style={styles.reporteTexto}>
                            {reporteManual.texto}
                        </div>
                        {reporteManual.audio_url && (
                            <div style={{marginTop: '20px'}}>
                                <p style={{fontSize: '12px', fontWeight: 'bold', marginBottom: '5px'}}>🔊 Escuchar reporte (gTTS):</p>
                                <audio controls src={reporteManual.audio_url} style={{width: '100%', height: '40px'}}></audio>
                            </div>
                        )}
                    </div>
                )}
            </div>
            
            {/* Animación Keyframes embebidos */}
            <style>
                {`
                @keyframes pulse {
                    0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
                    70% { transform: scale(1.05); box-shadow: 0 0 0 15px rgba(239, 68, 68, 0); }
                    100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
                }
                `}
            </style>
        </div>
    );
};

const styles = {
    page: { padding: '32px 40px', backgroundColor: '#f8fafc', minHeight: '100vh', fontFamily: '"Inter", sans-serif' },
    header: { marginBottom: '24px' },
    title: { fontSize: '28px', fontWeight: '800', color: '#0f172a', margin: 0 },
    subtitle: { fontSize: '15px', color: '#64748b', marginTop: '6px' },
    card: { backgroundColor: 'white', padding: '32px', borderRadius: '16px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)' },
    sectionTitle: { fontSize: '18px', fontWeight: '700', color: '#0f172a', margin: '0 0 8px 0' },
    
    // Voice UI
    voiceContainer: { display: 'flex', alignItems: 'center', gap: '20px', backgroundColor: '#f1f5f9', padding: '16px', borderRadius: '16px', border: '1px solid #cbd5e1' },
    micButton: { width: '64px', height: '64px', borderRadius: '50%', border: 'none', color: 'white', fontSize: '24px', cursor: 'pointer', display: 'flex', justifyContent: 'center', alignItems: 'center', transition: 'background-color 0.2s', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' },
    transcriptBox: { flex: 1, padding: '16px', backgroundColor: 'white', borderRadius: '12px', fontSize: '16px', minHeight: '56px', display: 'flex', alignItems: 'center', border: '1px solid #e2e8f0' },
    filtrosBox: { marginTop: '20px', padding: '20px', backgroundColor: '#f8fafc', borderRadius: '12px', border: '1px dashed #cbd5e1' },
    chip: { backgroundColor: '#e0e7ff', color: '#4338ca', padding: '6px 12px', borderRadius: '20px', fontSize: '13px', fontWeight: '600' },

    // Formulario Manual
    formRow: { display: 'flex', gap: '20px', alignItems: 'flex-start', flexWrap: 'wrap', marginTop: '20px' },
    formGroup: { display: 'flex', flexDirection: 'column', minWidth: '200px' },
    label: { fontSize: '12px', fontWeight: '700', color: '#64748b', marginBottom: '8px', textTransform: 'uppercase' },
    input: { padding: '12px 16px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '14px', outline: 'none' },
    checkboxRow: { display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 0' },
    btnPrimary: { backgroundColor: '#0f172a', color: 'white', padding: '12px 28px', borderRadius: '8px', border: 'none', fontWeight: '600', fontSize: '14px', cursor: 'pointer', transition: '0.2s' },
    
    reporteContainer: { marginTop: '24px', padding: '24px', backgroundColor: '#eff6ff', borderRadius: '12px', border: '1px solid #bfdbfe' },
    reporteTexto: { fontSize: '15px', color: '#1e293b', lineHeight: '1.6', whiteSpace: 'pre-wrap' },
};

export default ReportesFinancieros;
