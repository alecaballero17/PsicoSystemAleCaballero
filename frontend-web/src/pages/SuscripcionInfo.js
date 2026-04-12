// [SPRINT 1 - T025] Interfaz de monitoreo de límites SaaS.
// Componente de visualización de Suscripción para el Administrador de la Clínica.

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/axiosConfig';
import authService from '../services/authService';

export const SuscripcionInfo = () => {
    const navigate = useNavigate();
    const [info, setInfo] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchSuscripcionData = async () => {
            try {
                // Obtenemos el perfil del usuario para sacar su clinica_id (Tenant)
                const user = await authService.getCurrentUser(localStorage.getItem('token'));
                if (!user.clinica) {
                    setError('No tienes una clínica asignada, o eres SuperAdmin.');
                    setLoading(false);
                    return;
                }

                // Consumimos el endpoint de detalle de suscripción del Tenant
                const response = await apiClient.get(`suscripciones/${user.clinica}/`);
                setInfo(response.data);
            } catch (err) {
                console.error(err);
                setError('Error al obtener la información de la suscripción.');
            } finally {
                setLoading(false);
            }
        };

        fetchSuscripcionData();
    }, []);

    // Helper de estado y color
    const getBadgeStyle = (estado) => {
        switch (estado) {
            case 'ACTIVA': return { backgroundColor: '#dcfce7', color: '#166534', padding: '5px 10px', borderRadius: '12px', fontWeight: 'bold' };
            case 'SUSPENDIDA': return { backgroundColor: '#fee2e2', color: '#991b1b', padding: '5px 10px', borderRadius: '12px', fontWeight: 'bold' };
            case 'TRIAL': return { backgroundColor: '#fef3c7', color: '#92400e', padding: '5px 10px', borderRadius: '12px', fontWeight: 'bold' };
            default: return { backgroundColor: '#f1f5f9', color: '#475569', padding: '5px 10px', borderRadius: '12px', fontWeight: 'bold' };
        }
    };

    return (
        <div style={styles.container}>
            <header style={styles.header}>
                <div>
                    <h1 style={styles.headerTitle}>Mi Suscripción (SaaS)</h1>
                    <p style={styles.headerSubtitle}>Monitoreo de Límites y Plan Activo</p>
                </div>
                <button style={styles.btnSecondary} onClick={() => navigate('/dashboard')}>
                    Volver al Dashboard
                </button>
            </header>

            {loading ? (
                <div style={{ textAlign: 'center', marginTop: '50px' }}>
                    <p style={{ color: '#64748b' }}>Consultando estado de suscripción...</p>
                </div>
            ) : error ? (
                <div style={styles.errorBox}>{error}</div>
            ) : info?.estado === 'SIN_SUSCRIPCION' ? (
                <div style={styles.card}>
                    <h2 style={{ margin: '0 0 10px 0', color: '#0f172a' }}>{info.clinica_nombre}</h2>
                    <p style={{ color: '#ef4444', fontWeight: '500' }}>{info.mensaje}</p>
                </div>
            ) : (
                <div style={styles.card}>
                    <h2 style={{ margin: '0 0 20px 0', color: '#0f172a' }}>Clínica: {info.clinica_nombre}</h2>
                    
                    <div style={styles.grid}>
                        <div style={styles.infoBlock}>
                            <p style={styles.label}>Plan Actual</p>
                            <p style={styles.value}>{info.plan_nombre}</p>
                        </div>
                        <div style={styles.infoBlock}>
                            <p style={styles.label}>Estado</p>
                            <span style={getBadgeStyle(info.estado)}>
                                {info.estado} {info.estado === 'ACTIVA' ? '✅' : ''}
                            </span>
                        </div>
                        <div style={styles.infoBlock}>
                            <p style={styles.label}>Fecha de Inicio</p>
                            <p style={{ ...styles.value, fontSize: '16px' }}>{new Date(info.fecha_inicio).toLocaleDateString()}</p>
                        </div>
                    </div>

                    <hr style={{ margin: '30px 0', border: 'none', borderTop: '1px solid #e2e8f0' }} />

                    <h3 style={{ margin: '0 0 20px 0', color: '#334155' }}>Límites de Uso (Uso de Cupos)</h3>
                    
                    <div style={styles.limitsGrid}>
                        {/* Cupo Pacientes */}
                        <div style={styles.limitBox}>
                            <div style={{ fontSize: '32px', marginBottom: '10px' }}>🏃</div>
                            <p style={styles.limitTitle}>Pacientes Registrados</p>
                            <p style={styles.limitRatio}>
                                <span style={styles.actual}>{info.uso.pacientes_actuales}</span>
                                <span style={styles.divider}>/</span>
                                <span style={styles.maximo}>{info.uso.pacientes_limite}</span>
                            </p>
                            <div style={styles.progressBarBg}>
                                <div style={{
                                    ...styles.progressBarFill,
                                    width: `${Math.min(100, (info.uso.pacientes_actuales / info.uso.pacientes_limite) * 100)}%`,
                                    backgroundColor: (info.uso.pacientes_actuales >= info.uso.pacientes_limite) ? '#ef4444' : '#2563eb'
                                }} />
                            </div>
                        </div>

                        {/* Cupo Psicólogos */}
                        <div style={styles.limitBox}>
                            <div style={{ fontSize: '32px', marginBottom: '10px' }}>⚕️</div>
                            <p style={styles.limitTitle}>Psicólogos del Tenant</p>
                            <p style={styles.limitRatio}>
                                <span style={styles.actual}>{info.uso.psicologos_actuales}</span>
                                <span style={styles.divider}>/</span>
                                <span style={styles.maximo}>{info.uso.psicologos_limite}</span>
                            </p>
                            <div style={styles.progressBarBg}>
                                <div style={{
                                    ...styles.progressBarFill,
                                    width: `${Math.min(100, (info.uso.psicologos_actuales / info.uso.psicologos_limite) * 100)}%`,
                                    backgroundColor: (info.uso.psicologos_actuales >= info.uso.psicologos_limite) ? '#ef4444' : '#16a34a'
                                }} />
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

// ===============================================
// ESTILOS
// ===============================================
const styles = {
    container: { padding: '30px', maxWidth: '900px', margin: '0 auto', backgroundColor: '#f8fafc', minHeight: '100vh' },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' },
    headerTitle: { margin: 0, fontSize: '24px', color: '#0f172a' },
    headerSubtitle: { margin: 0, fontSize: '14px', color: '#64748b' },
    btnSecondary: { backgroundColor: '#fff', color: '#475569', padding: '10px 16px', border: '1px solid #cbd5e1', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' },
    errorBox: { padding: '15px', backgroundColor: '#fef2f2', color: '#b91c1c', border: '1px solid #fecaca', borderRadius: '8px' },
    card: { backgroundColor: 'white', borderRadius: '16px', padding: '40px', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)', },
    grid: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px' },
    infoBlock: { padding: '15px', backgroundColor: '#f8fafc', borderRadius: '12px', border: '1px solid #e2e8f0' },
    label: { margin: '0 0 5px 0', fontSize: '12px', color: '#64748b', textTransform: 'uppercase', fontWeight: 'bold' },
    value: { margin: 0, fontSize: '20px', fontWeight: 'bold', color: '#1e293b' },
    limitsGrid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' },
    limitBox: { border: '1px solid #e2e8f0', borderRadius: '16px', padding: '25px', textAlign: 'center', backgroundColor: '#fafaf9' },
    limitTitle: { margin: '0 0 15px 0', fontSize: '15px', fontWeight: 'bold', color: '#475569' },
    limitRatio: { margin: '0 0 15px 0', display: 'flex', justifyContent: 'center', alignItems: 'baseline', gap: '8px' },
    actual: { fontSize: '36px', fontWeight: '900', color: '#0f172a' },
    divider: { fontSize: '24px', color: '#cbd5e1', fontWeight: '300' },
    maximo: { fontSize: '20px', color: '#94a3b8', fontWeight: 'bold' },
    progressBarBg: { width: '100%', height: '8px', backgroundColor: '#e2e8f0', borderRadius: '4px', overflow: 'hidden' },
    progressBarFill: { height: '100%', borderRadius: '4px', transition: 'width 0.5s ease-out' }
};

export default SuscripcionInfo;
