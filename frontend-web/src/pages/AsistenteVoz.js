import React, { useState } from 'react';
import apiClient from '../api/axiosConfig';

const AsistenteVoz = () => {
    const [listening, setListening] = useState(false);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const startListening = () => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert("Tu navegador no soporta reconocimiento de voz. Usa Chrome.");
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.lang = 'es-BO';
        recognition.start();
        setListening(true);
        setError(null);

        recognition.onresult = async (event) => {
            const transcript = event.results[0][0].transcript;
            setListening(false);
            processQuery(transcript);
        };

        recognition.onerror = () => {
            setListening(false);
            setError("Error al capturar audio.");
        };
    };

    const processQuery = async (query) => {
        setLoading(true);
        try {
            const response = await apiClient.post('ia/voz-reporte/', { query });
            setResult(response.data);
            speak(response.data.summary);
        } catch (err) {
            setError("No pude procesar tu solicitud.");
        } finally {
            setLoading(false);
        }
    };

    const speak = (text) => {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'es-ES';
        window.speechSynthesis.speak(utterance);
    };

    return (
        <div style={styles.container}>
            <header style={styles.header}>
                <h2 style={styles.title}>🎙️ ASISTENTE DE VOZ INTELIGENTE (REPORTE VIP)</h2>
                <p style={styles.subtitle}>El jefe pide, la IA responde.</p>
            </header>

            <div style={styles.micCard}>
                <button 
                    style={{
                        ...styles.micBtn,
                        backgroundColor: listening ? '#ef4444' : '#2563eb',
                        transform: listening ? 'scale(1.1)' : 'scale(1)'
                    }} 
                    onClick={startListening}
                    disabled={loading}
                >
                    {listening ? '👂 Escuchando...' : '🎤 Presiona y Habla'}
                </button>
                <p style={styles.hint}>Prueba: "Dime las citas de la primera semana de mayo"</p>
            </div>

            {loading && <div style={styles.loading}>Procesando con Groq (Llama 3)...</div>}

            {result && result.params && (
                <div style={styles.resultCard}>
                    <div style={styles.summaryBox}>
                        <h3>🔊 Resumen Narrado:</h3>
                        <p>{result.summary}</p>
                    </div>
                    
                    <div style={styles.tableBox}>
                        <h3>📊 Datos Encontrados ({result.params.entidad}):</h3>
                        <table style={styles.table}>
                            <thead>
                                <tr>
                                    {result.params.entidad === 'citas' ? (
                                        <><th>Paciente</th><th>Fecha</th><th>Estado</th></>
                                    ) : (
                                        <><th>Monto</th><th>Concepto</th></>
                                    )}
                                </tr>
                            </thead>
                            <tbody>
                                {result.results && result.results.map((item, i) => (
                                    <tr key={i}>
                                        {result.params.entidad === 'citas' ? (
                                            <><td>{item.paciente}</td><td>{item.fecha}</td><td>{item.estado}</td></>
                                        ) : (
                                            <><td>{item.monto} BS</td><td>{item.concepto}</td></>
                                        )}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {result && !result.params && (
                <div style={styles.resultCard}>
                     <div style={{...styles.summaryBox, backgroundColor: '#fee2e2', borderLeft: '5px solid #ef4444'}}>
                        <h3>⚠️ Nota del Asistente:</h3>
                        <p>{result.summary}</p>
                    </div>
                </div>
            )}

            {error && <div style={styles.error}>{error}</div>}
        </div>
    );
};

const styles = {
    container: { padding: '40px', backgroundColor: '#f1f5f9', minHeight: '100vh' },
    header: { textAlign: 'center', marginBottom: '40px' },
    title: { fontSize: '28px', color: '#1e293b', fontWeight: 'bold' },
    subtitle: { color: '#64748b' },
    micCard: { backgroundColor: 'white', padding: '40px', borderRadius: '20px', textAlign: 'center', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' },
    micBtn: { width: '150px', height: '150px', borderRadius: '50%', border: 'none', color: 'white', fontSize: '18px', fontWeight: 'bold', cursor: 'pointer', transition: 'all 0.3s' },
    hint: { marginTop: '20px', color: '#94a3b8', fontStyle: 'italic' },
    loading: { textAlign: 'center', marginTop: '20px', fontWeight: 'bold', color: '#2563eb' },
    resultCard: { marginTop: '30px', animation: 'fadeIn 0.5s' },
    summaryBox: { backgroundColor: '#dcfce7', padding: '20px', borderRadius: '12px', marginBottom: '20px', borderLeft: '5px solid #22c55e' },
    tableBox: { backgroundColor: 'white', padding: '20px', borderRadius: '12px' },
    table: { width: '100%', borderCollapse: 'collapse' },
    error: { marginTop: '20px', color: '#ef4444', textAlign: 'center' }
};

export default AsistenteVoz;
