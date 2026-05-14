import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import apiClient from '../api/axiosConfig';

const DiagnosticoIA = () => {
    const [searchParams] = useSearchParams();
    const [pacienteId, setPacienteId] = useState(searchParams.get('paciente') || '');
    const [notas, setNotas] = useState('');
    const [loading, setLoading] = useState(false);
    const [resultado, setResultado] = useState(null);
    const [historial, setHistorial] = useState([]);

    useEffect(() => {
        fetchHistorial();
    }, []);

    const fetchHistorial = async () => {
        try {
            const response = await apiClient.get('ia/diagnostico/');
            setHistorial(response.data);
        } catch (err) {
            console.error("Error al cargar historial IA", err);
        }
    };

    const handleAnalizar = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const payload = {
                notas: notas,
                paciente_id: pacienteId || null
            };
            const response = await apiClient.post('ia/diagnostico/', payload);
            setResultado(response.data.diagnostico_ia);
            
            if ("Notification" in window) {
                if (Notification.permission === "granted") {
                    new Notification("Gemini AI", { body: "El diagnóstico clínico ha sido generado con éxito.", icon: "/favicon.ico" });
                }
            }
            
            fetchHistorial();
        } catch (err) {
            alert("Error al procesar con IA: " + (err.response?.data?.detail || err.message));
        } finally {
            setLoading(false);
        }
    };

    const formatMarkdown = (text) => {
        if (!text) return null;
        return text.split('\n').map((line, index) => {
            if (line.trim() === '') return <br key={index} />;
            
            // Títulos H3
            if (line.startsWith('### ')) {
                return <h4 key={index} style={{ color: '#4c1d95', margin: '15px 0 5px 0', borderBottom: '1px solid #ddd6fe', paddingBottom: '5px' }}>{line.replace('### ', '')}</h4>;
            }
            
            // Negritas
            const parts = line.split(/(\*\*.*?\*\*)/g);
            return (
                <div key={index} style={{ marginBottom: '8px' }}>
                    {parts.map((part, i) => {
                        if (part.startsWith('**') && part.endsWith('**')) {
                            return <strong key={i} style={{ color: '#312e81' }}>{part.slice(2, -2)}</strong>;
                        }
                        return part;
                    })}
                </div>
            );
        });
    };

    return (
        <div style={styles.container}>
            <h2 style={styles.title}>DIAGNÓSTICO ASISTIDO POR IA (GEMINI 2.0)</h2>
            
            <div style={styles.grid}>
                {/* Panel de Entrada */}
                <div style={styles.card}>
                    <h3 style={styles.cardTitle}>Nuevo Análisis</h3>
                    <form onSubmit={handleAnalizar}>
                        <div style={styles.inputGroup}>
                            <label style={styles.label}>ID PACIENTE (OPCIONAL)</label>
                            <input 
                                type="text" 
                                style={styles.input} 
                                value={pacienteId} 
                                onChange={(e) => setPacienteId(e.target.value)}
                            />
                        </div>
                        <div style={styles.inputGroup}>
                            <label style={styles.label}>NOTAS CLÍNICAS / SÍNTOMAS</label>
                            <textarea 
                                style={styles.textarea} 
                                placeholder="Describe los síntomas o notas del paciente aquí..."
                                value={notas}
                                onChange={(e) => setNotas(e.target.value)}
                                required
                            />
                        </div>
                        <button 
                            type="submit" 
                            style={styles.btnAi} 
                            disabled={loading || notas.length < 20}
                        >
                            {loading ? 'PROCESANDO CON GEMINI...' : '✨ GENERAR DIAGNÓSTICO'}
                        </button>
                    </form>

                    {resultado && (
                        <div style={styles.resultBox}>
                            <h4 style={styles.resultTitle}>Análisis Sugerido:</h4>
                            <div style={styles.resultText}>{formatMarkdown(resultado)}</div>
                        </div>
                    )}
                </div>

                {/* Historial */}
                <div style={styles.card}>
                    <h3 style={styles.cardTitle}>Historial Reciente</h3>
                    <div style={styles.list}>
                        {historial.map(h => (
                            <div key={h.id} style={styles.historyItem}>
                                <div style={styles.historyHeader}>
                                    <strong>{h.paciente}</strong>
                                    <span>{h.fecha_analisis}</span>
                                </div>
                                <p style={styles.historyBrief}>{h.resultado_ia.substring(0, 150)}...</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

const styles = {
    container: { padding: '40px', backgroundColor: '#f1f5f9', minHeight: '100vh' },
    title: { color: '#0f172a', marginBottom: '30px', fontWeight: 'bold' },
    grid: { display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '30px' },
    card: { backgroundColor: 'white', padding: '25px', borderRadius: '15px', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' },
    cardTitle: { marginTop: 0, marginBottom: '20px', fontSize: '16px', color: '#64748b' },
    inputGroup: { marginBottom: '20px' },
    label: { display: 'block', fontSize: '11px', fontWeight: 'bold', color: '#94a3b8', marginBottom: '8px' },
    input: { width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' },
    textarea: { width: '100%', minHeight: '150px', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0', fontFamily: 'inherit' },
    btnAi: { width: '100%', padding: '15px', backgroundColor: '#8b5cf6', color: 'white', border: 'none', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer' },
    resultBox: { marginTop: '25px', padding: '20px', backgroundColor: '#f5f3ff', borderRadius: '10px', border: '1px solid #ddd6fe' },
    resultTitle: { marginTop: 0, color: '#5b21b6', fontSize: '14px' },
    resultText: { fontSize: '14px', color: '#4c1d95', whiteSpace: 'pre-wrap', lineHeight: '1.6' },
    list: { display: 'flex', flexDirection: 'column', gap: '15px' },
    historyItem: { padding: '15px', borderBottom: '1px solid #f1f5f9' },
    historyHeader: { display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '5px' },
    historyBrief: { fontSize: '12px', color: '#64748b', margin: 0 }
};

export default DiagnosticoIA;
