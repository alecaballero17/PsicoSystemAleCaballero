// [SPRINT 4 - T062] Visualización cronológica del historial clínico del paciente (CU29)
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import apiClient from '../api/axiosConfig';
import { dashboardStyles as styles } from '../styles/dashboardStyles';

const ANIMO_COLORS = {
    BUENO: { bg: '#dcfce7', color: '#166534', icon: '😊' },
    REGULAR: { bg: '#fef9c3', color: '#854d0e', icon: '😐' },
    MALO: { bg: '#fee2e2', color: '#991b1b', icon: '😟' },
    CRITICO: { bg: '#fecaca', color: '#7f1d1d', icon: '🔴' },
};

const HistorialClinico = () => {
    const { pacienteId } = useParams();
    const navigate = useNavigate();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchHistorial = async () => {
            try {
                setLoading(true);
                const response = await apiClient.get(`pacientes/${pacienteId}/historial/`);
                setData(response.data);
            } catch (err) {
                console.error("Error al cargar historial", err);
            } finally {
                setLoading(false);
            }
        };
        fetchHistorial();
    }, [pacienteId]);

    if (loading) return (
        <div style={{ ...styles.layout, justifyContent: 'center', alignItems: 'center' }}>
            <div style={{ textAlign: 'center', color: '#64748b' }}>
                <div style={{ fontSize: '40px', marginBottom: '10px' }}>⏳</div>
                <p style={{ fontSize: '16px' }}>Cargando historial clínico...</p>
            </div>
        </div>
    );

    if (!data) return (
        <div style={{ ...styles.layout, justifyContent: 'center', alignItems: 'center' }}>
            <div style={{ textAlign: 'center', color: '#dc2626' }}>
                <p>No se encontró información del paciente.</p>
                <button onClick={() => navigate('/pacientes')} style={{ padding: '10px 20px', background: '#2563eb', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', marginTop: '10px' }}>
                    Volver a Pacientes
                </button>
            </div>
        </div>
    );

    const { paciente, diagnostico_global, evoluciones } = data;

    return (
        <div style={{ padding: '30px', backgroundColor: '#f1f5f9', minHeight: '100vh', fontFamily: '"Inter", sans-serif' }}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '25px' }}>
                <div>
                    <button onClick={() => navigate('/pacientes')} style={{ background: 'none', border: 'none', color: '#2563eb', cursor: 'pointer', fontSize: '14px', marginBottom: '8px' }}>
                        ← Volver a Gestión de Pacientes
                    </button>
                    <h1 style={{ margin: 0, fontSize: '26px', color: '#0f172a' }}>📋 Historial Clínico</h1>
                    <p style={{ margin: '4px 0 0 0', color: '#64748b', fontSize: '14px' }}>
                        Paciente: <strong>{paciente.nombre}</strong> — CI: {paciente.ci}
                    </p>
                </div>
                <button
                    onClick={() => navigate(`/registro-evolucion/${pacienteId}`)}
                    style={{ padding: '12px 24px', background: '#2563eb', color: 'white', border: 'none', borderRadius: '10px', cursor: 'pointer', fontWeight: 'bold', fontSize: '14px', boxShadow: '0 4px 6px rgba(37, 99, 235, 0.3)' }}
                >
                    ➕ Registrar Evolución
                </button>
            </div>

            {/* Info del Paciente */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '25px' }}>
                <div style={{ background: 'white', borderRadius: '16px', padding: '22px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
                    <h3 style={{ margin: '0 0 15px 0', fontSize: '16px', color: '#0f172a' }}>👤 Datos del Paciente</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '13px', color: '#475569' }}>
                        <div><strong>Nombre:</strong> {paciente.nombre}</div>
                        <div><strong>CI:</strong> {paciente.ci}</div>
                        <div><strong>Nacimiento:</strong> {paciente.fecha_nacimiento}</div>
                        <div><strong>Teléfono:</strong> {paciente.telefono}</div>
                        <div style={{ gridColumn: '1/3' }}><strong>Motivo Consulta:</strong> {paciente.motivo_consulta || 'No especificado'}</div>
                    </div>
                </div>

                {/* Diagnóstico Global */}
                <div style={{ background: diagnostico_global ? '#f0fdf4' : '#fffbeb', borderRadius: '16px', padding: '22px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)', border: diagnostico_global ? '1px solid #bbf7d0' : '1px solid #fde68a' }}>
                    <h3 style={{ margin: '0 0 15px 0', fontSize: '16px', color: '#0f172a' }}>🩺 Diagnóstico del Tratamiento</h3>
                    {diagnostico_global ? (
                        <div style={{ fontSize: '13px', color: '#475569' }}>
                            <div style={{ marginBottom: '8px' }}>
                                <strong>Diagnóstico Inicial:</strong>
                                <p style={{ margin: '4px 0', padding: '8px 12px', background: 'white', borderRadius: '8px', border: '1px solid #e2e8f0' }}>{diagnostico_global.diagnostico_inicial}</p>
                            </div>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '8px' }}>
                                <div><strong>Fecha Inicio:</strong> {diagnostico_global.fecha_inicio}</div>
                                <div><strong>Estado:</strong> <span style={{ padding: '2px 8px', borderRadius: '20px', fontSize: '11px', fontWeight: 'bold', background: diagnostico_global.estado === 'EN_TRATAMIENTO' ? '#dbeafe' : diagnostico_global.estado === 'ALTA' ? '#dcfce7' : '#fee2e2', color: diagnostico_global.estado === 'EN_TRATAMIENTO' ? '#1e40af' : diagnostico_global.estado === 'ALTA' ? '#166534' : '#991b1b' }}>{diagnostico_global.estado_display}</span></div>
                            </div>
                            {diagnostico_global.diagnostico_final && (
                                <div style={{ marginBottom: '8px' }}>
                                    <strong>Diagnóstico Final:</strong>
                                    <p style={{ margin: '4px 0', padding: '8px 12px', background: 'white', borderRadius: '8px', border: '1px solid #e2e8f0' }}>{diagnostico_global.diagnostico_final}</p>
                                </div>
                            )}
                            {diagnostico_global.fecha_fin && (
                                <div><strong>Fecha Fin:</strong> {diagnostico_global.fecha_fin}</div>
                            )}
                        </div>
                    ) : (
                        <div style={{ textAlign: 'center', color: '#92400e', fontSize: '13px' }}>
                            <p>⚠️ Este paciente aún no tiene un diagnóstico registrado.</p>
                            <button
                                onClick={() => navigate(`/registro-evolucion/${pacienteId}`)}
                                style={{ padding: '8px 16px', background: '#f59e0b', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', fontSize: '12px' }}
                            >
                                Registrar Diagnóstico
                            </button>
                        </div>
                    )}
                </div>
            </div>

            {/* Timeline de Evoluciones */}
            <div style={{ background: 'white', borderRadius: '16px', padding: '25px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
                <h3 style={{ margin: '0 0 20px 0', fontSize: '18px', color: '#0f172a' }}>📈 Evoluciones Clínicas ({evoluciones.length})</h3>

                {evoluciones.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>
                        <div style={{ fontSize: '50px', marginBottom: '10px' }}>📝</div>
                        <p>No hay evoluciones registradas aún.</p>
                        <button
                            onClick={() => navigate(`/registro-evolucion/${pacienteId}`)}
                            style={{ padding: '10px 20px', background: '#2563eb', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', marginTop: '10px' }}
                        >
                            Registrar Primera Evolución
                        </button>
                    </div>
                ) : (
                    <div style={{ position: 'relative', paddingLeft: '40px' }}>
                        {/* Línea vertical del timeline */}
                        <div style={{ position: 'absolute', left: '16px', top: '0', bottom: '0', width: '3px', background: 'linear-gradient(to bottom, #3b82f6, #8b5cf6, #06b6d4)', borderRadius: '3px' }} />

                        {evoluciones.map((evo, index) => {
                            const animoStyle = ANIMO_COLORS[evo.estado_animo] || ANIMO_COLORS.REGULAR;
                            return (
                                <div key={evo.id} style={{ position: 'relative', marginBottom: '24px', animation: `fadeIn 0.4s ease ${index * 0.1}s both` }}>
                                    {/* Dot del timeline */}
                                    <div style={{
                                        position: 'absolute', left: '-33px', top: '8px',
                                        width: '14px', height: '14px', borderRadius: '50%',
                                        background: 'white', border: '3px solid #3b82f6',
                                        boxShadow: '0 0 0 4px rgba(59, 130, 246, 0.15)'
                                    }} />

                                    <div style={{ background: '#f8fafc', borderRadius: '12px', padding: '18px', border: '1px solid #e2e8f0', transition: 'box-shadow 0.2s' }}>
                                        {/* Header */}
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                                <span style={{ fontSize: '14px', fontWeight: 'bold', color: '#0f172a' }}>📅 {evo.fecha_sesion}</span>
                                                <span style={{ padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 'bold', background: animoStyle.bg, color: animoStyle.color }}>
                                                    {animoStyle.icon} {evo.estado_animo_display}
                                                </span>
                                            </div>
                                            <span style={{ fontSize: '11px', color: '#94a3b8' }}>Psic. {evo.psicologo_nombre || 'N/A'}</span>
                                        </div>

                                        {/* Contenido */}
                                        <div style={{ fontSize: '13px', color: '#475569' }}>
                                            <div style={{ marginBottom: '8px' }}>
                                                <strong style={{ color: '#1e293b' }}>Diagnóstico:</strong>
                                                <p style={{ margin: '4px 0', lineHeight: '1.5' }}>{evo.diagnostico}</p>
                                            </div>
                                            {evo.observaciones && (
                                                <div style={{ marginBottom: '8px' }}>
                                                    <strong style={{ color: '#1e293b' }}>Observaciones:</strong>
                                                    <p style={{ margin: '4px 0', lineHeight: '1.5' }}>{evo.observaciones}</p>
                                                </div>
                                            )}
                                            {evo.recomendacion && (
                                                <div style={{ marginTop: '10px', padding: '10px 14px', background: '#eff6ff', borderRadius: '8px', borderLeft: '4px solid #3b82f6' }}>
                                                    <strong style={{ color: '#1e40af', fontSize: '12px' }}>💡 Recomendación del Psicólogo:</strong>
                                                    <p style={{ margin: '4px 0', color: '#1e3a5f', lineHeight: '1.5' }}>{evo.recomendacion}</p>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* CSS animation */}
            <style>{`
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(15px); }
                    to { opacity: 1; transform: translateY(0); }
                }
            `}</style>
        </div>
    );
};

export default HistorialClinico;
