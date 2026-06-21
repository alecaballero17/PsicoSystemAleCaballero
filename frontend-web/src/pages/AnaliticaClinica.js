// [SPRINT 4 - T071] Dashboard de Analítica Clínica (CU22)
// Métricas de tratamientos, distribución de estados de ánimo y resultados IA.
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/axiosConfig';

const AnaliticaClinica = () => {
    const navigate = useNavigate();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAnalitica = async () => {
            try {
                setLoading(true);
                const response = await apiClient.get('analitica-clinica/');
                setData(response.data);
            } catch (err) {
                console.error("Error al cargar analítica", err);
            } finally {
                setLoading(false);
            }
        };
        fetchAnalitica();
    }, []);

    if (loading) return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontFamily: '"Inter", sans-serif', color: '#64748b' }}>
            <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '40px', marginBottom: '10px' }}>📊</div>
                <p>Cargando analítica clínica...</p>
            </div>
        </div>
    );

    if (!data) return null;

    const ANIMO_LABELS = { BUENO: 'Bueno 😊', REGULAR: 'Regular 😐', MALO: 'Malo 😟', CRITICO: 'Crítico 🔴' };
    const ANIMO_COLORS = { BUENO: '#22c55e', REGULAR: '#eab308', MALO: '#ef4444', CRITICO: '#7f1d1d' };

    const totalAnimo = data.estados_animo.reduce((acc, e) => acc + e.total, 0) || 1;

    const metricCards = [
        { label: 'Total Pacientes', value: data.total_pacientes, icon: '👥', color: '#3b82f6' },
        { label: 'En Tratamiento', value: data.en_tratamiento, icon: '🩺', color: '#22c55e' },
        { label: 'Alta Médica', value: data.alta, icon: '✅', color: '#06b6d4' },
        { label: 'Abandono', value: data.abandono, icon: '⚠️', color: '#f59e0b' },
        { label: 'Sin Diagnóstico', value: data.sin_diagnostico, icon: '📋', color: '#94a3b8' },
    ];

    const cardStyle = { background: 'white', borderRadius: '16px', padding: '24px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' };

    return (
        <div style={{ padding: '30px', backgroundColor: '#f1f5f9', minHeight: '100vh', fontFamily: '"Inter", sans-serif' }}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '25px' }}>
                <div>
                    <button onClick={() => navigate('/dashboard')} style={{ background: 'none', border: 'none', color: '#2563eb', cursor: 'pointer', fontSize: '14px', marginBottom: '8px' }}>
                        ← Volver al Dashboard
                    </button>
                    <h1 style={{ margin: 0, fontSize: '26px', color: '#0f172a' }}>📊 Analítica Clínica</h1>
                    <p style={{ margin: '4px 0 0 0', color: '#64748b', fontSize: '14px' }}>
                        Dashboard de patrones clínicos, evolución anímica y resultados de IA.
                    </p>
                </div>
            </div>

            {/* Metric Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '16px', marginBottom: '24px' }}>
                {metricCards.map((m, i) => (
                    <div key={i} style={{ ...cardStyle, padding: '20px', textAlign: 'center', borderTop: `4px solid ${m.color}`, animation: `fadeIn 0.4s ease ${i * 0.08}s both` }}>
                        <div style={{ fontSize: '28px', marginBottom: '6px' }}>{m.icon}</div>
                        <div style={{ fontSize: '30px', fontWeight: '800', color: m.color }}>{m.value}</div>
                        <div style={{ fontSize: '12px', color: '#64748b', marginTop: '4px', fontWeight: '600' }}>{m.label}</div>
                    </div>
                ))}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
                {/* Distribución de Estados de Ánimo */}
                <div style={cardStyle}>
                    <h3 style={{ margin: '0 0 20px 0', fontSize: '16px', color: '#0f172a' }}>🧠 Distribución de Estados de Ánimo</h3>
                    {data.estados_animo.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '30px', color: '#94a3b8' }}>
                            <p>No hay datos de evoluciones aún.</p>
                        </div>
                    ) : (
                        <div>
                            {data.estados_animo.map((ea, i) => {
                                const pct = Math.round((ea.total / totalAnimo) * 100);
                                const color = ANIMO_COLORS[ea.estado_animo] || '#94a3b8';
                                return (
                                    <div key={i} style={{ marginBottom: '14px' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', fontSize: '13px' }}>
                                            <span style={{ fontWeight: '600', color: '#334155' }}>{ANIMO_LABELS[ea.estado_animo] || ea.estado_animo}</span>
                                            <span style={{ color: '#64748b' }}>{ea.total} ({pct}%)</span>
                                        </div>
                                        <div style={{ width: '100%', height: '12px', background: '#f1f5f9', borderRadius: '6px', overflow: 'hidden' }}>
                                            <div style={{
                                                width: `${pct}%`, height: '100%', background: color,
                                                borderRadius: '6px', transition: 'width 0.8s ease',
                                                animation: `barGrow 0.8s ease ${i * 0.15}s both`
                                            }} />
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>

                {/* Distribución por Estado de Tratamiento - Gráfico Donut CSS */}
                <div style={cardStyle}>
                    <h3 style={{ margin: '0 0 20px 0', fontSize: '16px', color: '#0f172a' }}>📋 Estado de Tratamientos</h3>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '30px' }}>
                        {/* Visual donut */}
                        <div style={{ position: 'relative', width: '140px', height: '140px' }}>
                            <svg viewBox="0 0 36 36" style={{ width: '140px', height: '140px', transform: 'rotate(-90deg)' }}>
                                {(() => {
                                    const total = (data.en_tratamiento + data.alta + data.abandono + data.sin_diagnostico) || 1;
                                    const segments = [
                                        { value: data.en_tratamiento, color: '#22c55e' },
                                        { value: data.alta, color: '#06b6d4' },
                                        { value: data.abandono, color: '#f59e0b' },
                                        { value: data.sin_diagnostico, color: '#cbd5e1' },
                                    ];
                                    let offset = 0;
                                    return segments.map((seg, i) => {
                                        const pct = (seg.value / total) * 100;
                                        const el = (
                                            <circle key={i} cx="18" cy="18" r="15.915" fill="none"
                                                stroke={seg.color} strokeWidth="3.5"
                                                strokeDasharray={`${pct} ${100 - pct}`}
                                                strokeDashoffset={`-${offset}`}
                                            />
                                        );
                                        offset += pct;
                                        return el;
                                    });
                                })()}
                            </svg>
                            <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center' }}>
                                <div style={{ fontSize: '22px', fontWeight: '800', color: '#0f172a' }}>{data.total_pacientes}</div>
                                <div style={{ fontSize: '10px', color: '#64748b' }}>Total</div>
                            </div>
                        </div>
                        {/* Legend */}
                        <div style={{ fontSize: '13px' }}>
                            {[
                                { label: 'En tratamiento', value: data.en_tratamiento, color: '#22c55e' },
                                { label: 'Alta médica', value: data.alta, color: '#06b6d4' },
                                { label: 'Abandono', value: data.abandono, color: '#f59e0b' },
                                { label: 'Sin diagnóstico', value: data.sin_diagnostico, color: '#cbd5e1' },
                            ].map((item, i) => (
                                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                                    <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: item.color }} />
                                    <span style={{ color: '#475569' }}>{item.label}: <strong>{item.value}</strong></span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* Últimas Evoluciones */}
            <div style={{ ...cardStyle, marginBottom: '24px' }}>
                <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', color: '#0f172a' }}>📈 Últimas Evoluciones Registradas</h3>
                {data.ultimas_evoluciones.length === 0 ? (
                    <p style={{ color: '#94a3b8', textAlign: 'center', padding: '20px' }}>No hay evoluciones registradas aún.</p>
                ) : (
                    <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                            <thead>
                                <tr style={{ background: '#f8fafc', borderBottom: '2px solid #e2e8f0' }}>
                                    <th style={{ padding: '10px 12px', textAlign: 'left', color: '#64748b', fontWeight: '700' }}>Fecha</th>
                                    <th style={{ padding: '10px 12px', textAlign: 'left', color: '#64748b', fontWeight: '700' }}>Ánimo</th>
                                    <th style={{ padding: '10px 12px', textAlign: 'left', color: '#64748b', fontWeight: '700' }}>Diagnóstico</th>
                                    <th style={{ padding: '10px 12px', textAlign: 'left', color: '#64748b', fontWeight: '700' }}>Recomendación</th>
                                    <th style={{ padding: '10px 12px', textAlign: 'left', color: '#64748b', fontWeight: '700' }}>Psicólogo</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.ultimas_evoluciones.map((evo, i) => (
                                    <tr key={evo.id} style={{ borderBottom: '1px solid #f1f5f9', animation: `fadeIn 0.3s ease ${i * 0.05}s both` }}>
                                        <td style={{ padding: '10px 12px', fontWeight: '600' }}>{evo.fecha_sesion}</td>
                                        <td style={{ padding: '10px 12px' }}>
                                            <span style={{
                                                padding: '3px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 'bold',
                                                background: evo.estado_animo === 'BUENO' ? '#dcfce7' : evo.estado_animo === 'REGULAR' ? '#fef9c3' : evo.estado_animo === 'MALO' ? '#fee2e2' : '#fecaca',
                                                color: evo.estado_animo === 'BUENO' ? '#166534' : evo.estado_animo === 'REGULAR' ? '#854d0e' : '#991b1b',
                                            }}>
                                                {evo.estado_animo_display}
                                            </span>
                                        </td>
                                        <td style={{ padding: '10px 12px', maxWidth: '250px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{evo.diagnostico}</td>
                                        <td style={{ padding: '10px 12px', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: '#2563eb' }}>{evo.recomendacion || '—'}</td>
                                        <td style={{ padding: '10px 12px', color: '#64748b' }}>{evo.psicologo_nombre || '—'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Últimos Diagnósticos IA */}
            <div style={cardStyle}>
                <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', color: '#0f172a' }}>🤖 Últimos Análisis de IA (Gemini)</h3>
                {data.ultimos_ia.length === 0 ? (
                    <p style={{ color: '#94a3b8', textAlign: 'center', padding: '20px' }}>No hay análisis de IA registrados aún.</p>
                ) : (
                    <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                            <thead>
                                <tr style={{ background: '#f8fafc', borderBottom: '2px solid #e2e8f0' }}>
                                    <th style={{ padding: '10px 12px', textAlign: 'left', color: '#64748b', fontWeight: '700' }}>Fecha</th>
                                    <th style={{ padding: '10px 12px', textAlign: 'left', color: '#64748b', fontWeight: '700' }}>Paciente</th>
                                    <th style={{ padding: '10px 12px', textAlign: 'left', color: '#64748b', fontWeight: '700' }}>Resultado IA</th>
                                    <th style={{ padding: '10px 12px', textAlign: 'left', color: '#64748b', fontWeight: '700' }}>Confianza</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.ultimos_ia.map((ia, i) => (
                                    <tr key={ia.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                                        <td style={{ padding: '10px 12px', fontWeight: '600' }}>{ia.fecha_analisis ? new Date(ia.fecha_analisis).toLocaleDateString() : '—'}</td>
                                        <td style={{ padding: '10px 12px' }}>{ia.paciente__nombre || 'General'}</td>
                                        <td style={{ padding: '10px 12px', maxWidth: '350px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{ia.resultado_ia}</td>
                                        <td style={{ padding: '10px 12px' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                                <div style={{ width: '60px', height: '6px', background: '#f1f5f9', borderRadius: '3px', overflow: 'hidden' }}>
                                                    <div style={{ width: `${Math.round(ia.probabilidad_acierto * 100)}%`, height: '100%', background: ia.probabilidad_acierto > 0.7 ? '#22c55e' : '#f59e0b', borderRadius: '3px' }} />
                                                </div>
                                                <span style={{ fontSize: '11px', fontWeight: 'bold', color: '#64748b' }}>{Math.round(ia.probabilidad_acierto * 100)}%</span>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            <style>{`
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(12px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                @keyframes barGrow {
                    from { width: 0; }
                }
            `}</style>
        </div>
    );
};

export default AnaliticaClinica;
