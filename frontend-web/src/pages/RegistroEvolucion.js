// [SPRINT 4 - T063/T064] Formulario dinámico para registro de diagnósticos, evoluciones y recomendaciones (CU29)
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import apiClient from '../api/axiosConfig';

const RegistroEvolucion = () => {
    const { pacienteId } = useParams();
    const navigate = useNavigate();
    const [paciente, setPaciente] = useState(null);
    const [loading, setLoading] = useState(true);
    const [guardando, setGuardando] = useState(false);

    // Diagnóstico Global
    const [dxExistente, setDxExistente] = useState(null);
    const [dxForm, setDxForm] = useState({
        diagnostico_inicial: '',
        fecha_inicio: new Date().toISOString().split('T')[0],
        diagnostico_final: '',
        fecha_fin: '',
        estado: 'EN_TRATAMIENTO',
    });

    // Evolución
    const [evoForm, setEvoForm] = useState({
        fecha_sesion: new Date().toISOString().split('T')[0],
        diagnostico: '',
        observaciones: '',
        estado_animo: 'REGULAR',
        recomendacion: '',
    });

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                // Cargar datos del paciente y diagnóstico
                const [pacRes, dxRes] = await Promise.all([
                    apiClient.get(`pacientes/${pacienteId}/`),
                    apiClient.get(`clinica/diagnosticos/?paciente=${pacienteId}`),
                ]);
                setPaciente(pacRes.data);
                if (dxRes.data.length > 0) {
                    const dx = dxRes.data[0];
                    setDxExistente(dx);
                    setDxForm({
                        diagnostico_inicial: dx.diagnostico_inicial,
                        fecha_inicio: dx.fecha_inicio,
                        diagnostico_final: dx.diagnostico_final || '',
                        fecha_fin: dx.fecha_fin || '',
                        estado: dx.estado,
                    });
                }
            } catch (err) {
                console.error("Error cargando datos", err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [pacienteId]);

    const handleSaveDiagnostico = async () => {
        setGuardando(true);
        try {
            const payload = {
                paciente: parseInt(pacienteId),
                ...dxForm,
                fecha_fin: dxForm.fecha_fin || null,
            };

            if (dxExistente) {
                await apiClient.put(`clinica/diagnosticos/${dxExistente.id}/`, payload);
                alert('✅ Diagnóstico actualizado exitosamente.');
            } else {
                const res = await apiClient.post('clinica/diagnosticos/', payload);
                setDxExistente(res.data);
                alert('✅ Diagnóstico registrado exitosamente.');
            }
        } catch (err) {
            console.error(err);
            alert('❌ Error al guardar diagnóstico: ' + (err.response?.data ? JSON.stringify(err.response.data) : err.message));
        } finally {
            setGuardando(false);
        }
    };

    const handleSaveEvolucion = async (e) => {
        e.preventDefault();
        if (!evoForm.diagnostico.trim()) {
            alert('El campo de diagnóstico de la sesión es obligatorio.');
            return;
        }
        setGuardando(true);
        try {
            await apiClient.post('clinica/evoluciones/', {
                paciente: parseInt(pacienteId),
                ...evoForm,
            });
            alert('✅ Evolución registrada exitosamente.');
            setEvoForm({
                fecha_sesion: new Date().toISOString().split('T')[0],
                diagnostico: '',
                observaciones: '',
                estado_animo: 'REGULAR',
                recomendacion: '',
            });
        } catch (err) {
            console.error(err);
            alert('❌ Error al guardar evolución: ' + (err.response?.data ? JSON.stringify(err.response.data) : err.message));
        } finally {
            setGuardando(false);
        }
    };

    const inputStyle = {
        width: '100%', padding: '10px 14px', border: '1px solid #cbd5e1',
        borderRadius: '8px', fontSize: '14px', fontFamily: 'inherit',
        boxSizing: 'border-box', transition: 'border-color 0.2s',
        outline: 'none',
    };
    const textareaStyle = { ...inputStyle, minHeight: '80px', resize: 'vertical' };
    const labelStyle = { display: 'block', marginBottom: '5px', fontWeight: '600', fontSize: '13px', color: '#334155' };
    const fieldGroup = { marginBottom: '16px' };
    const cardStyle = { background: 'white', borderRadius: '16px', padding: '25px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)', marginBottom: '20px' };

    if (loading) return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontFamily: '"Inter", sans-serif', color: '#64748b' }}>
            <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '40px', marginBottom: '10px' }}>⏳</div>
                <p>Cargando formulario...</p>
            </div>
        </div>
    );

    return (
        <div style={{ padding: '30px', backgroundColor: '#f1f5f9', minHeight: '100vh', fontFamily: '"Inter", sans-serif' }}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '25px' }}>
                <div>
                    <button onClick={() => navigate(`/historial-clinico/${pacienteId}`)} style={{ background: 'none', border: 'none', color: '#2563eb', cursor: 'pointer', fontSize: '14px', marginBottom: '8px' }}>
                        ← Volver al Historial
                    </button>
                    <h1 style={{ margin: 0, fontSize: '24px', color: '#0f172a' }}>📝 Registro de Evolución Clínica</h1>
                    <p style={{ margin: '4px 0 0 0', color: '#64748b', fontSize: '14px' }}>
                        Paciente: <strong>{paciente?.nombre}</strong> — CI: {paciente?.ci}
                    </p>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', alignItems: 'start' }}>
                {/* COLUMNA IZQUIERDA: Diagnóstico Global */}
                <div style={{ ...cardStyle, border: '2px solid #dbeafe' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
                        <span style={{ fontSize: '22px' }}>🩺</span>
                        <h2 style={{ margin: 0, fontSize: '18px', color: '#0f172a' }}>Diagnóstico del Tratamiento</h2>
                    </div>
                    <p style={{ fontSize: '12px', color: '#64748b', marginBottom: '20px' }}>
                        {dxExistente ? '✅ Diagnóstico existente — puede actualizarlo.' : '⚠️ Este paciente aún no tiene diagnóstico global. Complete los campos para crearlo.'}
                    </p>

                    <div style={fieldGroup}>
                        <label style={labelStyle}>Diagnóstico Inicial *</label>
                        <textarea
                            value={dxForm.diagnostico_inicial}
                            onChange={e => setDxForm({...dxForm, diagnostico_inicial: e.target.value})}
                            style={textareaStyle}
                            placeholder="Describa el diagnóstico al inicio del tratamiento..."
                        />
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                        <div style={fieldGroup}>
                            <label style={labelStyle}>Fecha Inicio *</label>
                            <input type="date" value={dxForm.fecha_inicio} onChange={e => setDxForm({...dxForm, fecha_inicio: e.target.value})} style={inputStyle} />
                        </div>
                        <div style={fieldGroup}>
                            <label style={labelStyle}>Estado</label>
                            <select value={dxForm.estado} onChange={e => setDxForm({...dxForm, estado: e.target.value})} style={inputStyle}>
                                <option value="EN_TRATAMIENTO">En tratamiento</option>
                                <option value="ALTA">Alta</option>
                                <option value="ABANDONO">Abandono</option>
                            </select>
                        </div>
                    </div>

                    <div style={{ borderTop: '1px dashed #e2e8f0', paddingTop: '16px', marginTop: '8px' }}>
                        <p style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '12px' }}>Completar al finalizar el tratamiento:</p>
                        <div style={fieldGroup}>
                            <label style={labelStyle}>Diagnóstico Final</label>
                            <textarea
                                value={dxForm.diagnostico_final}
                                onChange={e => setDxForm({...dxForm, diagnostico_final: e.target.value})}
                                style={textareaStyle}
                                placeholder="Diagnóstico al cierre del tratamiento..."
                            />
                        </div>
                        <div style={fieldGroup}>
                            <label style={labelStyle}>Fecha Fin</label>
                            <input type="date" value={dxForm.fecha_fin} onChange={e => setDxForm({...dxForm, fecha_fin: e.target.value})} style={inputStyle} />
                        </div>
                    </div>

                    <button
                        onClick={handleSaveDiagnostico}
                        disabled={guardando || !dxForm.diagnostico_inicial.trim()}
                        style={{ width: '100%', padding: '12px', background: dxExistente ? '#059669' : '#2563eb', color: 'white', border: 'none', borderRadius: '10px', cursor: 'pointer', fontWeight: 'bold', fontSize: '14px', opacity: guardando ? 0.7 : 1, marginTop: '10px' }}
                    >
                        {guardando ? '⏳ Guardando...' : (dxExistente ? '💾 Actualizar Diagnóstico' : '➕ Crear Diagnóstico')}
                    </button>
                </div>

                {/* COLUMNA DERECHA: Nueva Evolución */}
                <div style={{ ...cardStyle, border: '2px solid #e0e7ff' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
                        <span style={{ fontSize: '22px' }}>📈</span>
                        <h2 style={{ margin: 0, fontSize: '18px', color: '#0f172a' }}>Nueva Evolución de Sesión</h2>
                    </div>
                    <p style={{ fontSize: '12px', color: '#64748b', marginBottom: '20px' }}>
                        Registre la evolución clínica de una cita o sesión con el paciente.
                    </p>

                    <form onSubmit={handleSaveEvolucion}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                            <div style={fieldGroup}>
                                <label style={labelStyle}>Fecha de Sesión *</label>
                                <input type="date" value={evoForm.fecha_sesion} onChange={e => setEvoForm({...evoForm, fecha_sesion: e.target.value})} style={inputStyle} required />
                            </div>
                            <div style={fieldGroup}>
                                <label style={labelStyle}>Estado de Ánimo *</label>
                                <div style={{ display: 'flex', gap: '6px' }}>
                                    {[
                                        { v: 'BUENO', icon: '😊', label: 'Bueno', color: '#16a34a' },
                                        { v: 'REGULAR', icon: '😐', label: 'Regular', color: '#ca8a04' },
                                        { v: 'MALO', icon: '😟', label: 'Malo', color: '#dc2626' },
                                        { v: 'CRITICO', icon: '🔴', label: 'Crítico', color: '#7f1d1d' },
                                    ].map(opt => (
                                        <button
                                            type="button"
                                            key={opt.v}
                                            onClick={() => setEvoForm({...evoForm, estado_animo: opt.v})}
                                            style={{
                                                flex: 1, padding: '8px 4px', borderRadius: '8px', cursor: 'pointer',
                                                border: evoForm.estado_animo === opt.v ? `2px solid ${opt.color}` : '1px solid #e2e8f0',
                                                background: evoForm.estado_animo === opt.v ? `${opt.color}15` : 'white',
                                                fontSize: '11px', fontWeight: evoForm.estado_animo === opt.v ? 'bold' : 'normal',
                                                color: opt.color, textAlign: 'center',
                                            }}
                                        >
                                            {opt.icon}<br/>{opt.label}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>

                        <div style={fieldGroup}>
                            <label style={labelStyle}>Diagnóstico de la Sesión *</label>
                            <textarea
                                value={evoForm.diagnostico}
                                onChange={e => setEvoForm({...evoForm, diagnostico: e.target.value})}
                                style={textareaStyle}
                                placeholder="Diagnóstico y hallazgos clínicos de esta sesión..."
                                required
                            />
                        </div>

                        <div style={fieldGroup}>
                            <label style={labelStyle}>Observaciones</label>
                            <textarea
                                value={evoForm.observaciones}
                                onChange={e => setEvoForm({...evoForm, observaciones: e.target.value})}
                                style={{ ...textareaStyle, minHeight: '60px' }}
                                placeholder="Notas adicionales de la sesión..."
                            />
                        </div>

                        <div style={{ ...fieldGroup, background: '#eff6ff', padding: '14px', borderRadius: '10px', border: '1px solid #bfdbfe' }}>
                            <label style={{ ...labelStyle, color: '#1e40af' }}>💡 Recomendación para el Paciente</label>
                            <textarea
                                value={evoForm.recomendacion}
                                onChange={e => setEvoForm({...evoForm, recomendacion: e.target.value})}
                                style={{ ...textareaStyle, minHeight: '70px', borderColor: '#93c5fd' }}
                                placeholder="Recomendación del psicólogo para esta sesión..."
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={guardando}
                            style={{ width: '100%', padding: '12px', background: '#4f46e5', color: 'white', border: 'none', borderRadius: '10px', cursor: 'pointer', fontWeight: 'bold', fontSize: '14px', opacity: guardando ? 0.7 : 1, marginTop: '6px', boxShadow: '0 4px 6px rgba(79, 70, 229, 0.3)' }}
                        >
                            {guardando ? '⏳ Guardando Evolución...' : '📋 Registrar Evolución'}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default RegistroEvolucion;
