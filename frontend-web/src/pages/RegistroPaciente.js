import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import pacienteService from '../services/pacienteService'; // Importamos la lógica
import { registroStyles as styles } from '../styles/registroStyles'; // Importamos los estilos

const RegistroPaciente = () => {
    const [formData, setFormData] = useState({ nombre: '', ci: '', fecha_nacimiento: '', telefono: '' });
    const [loading, setLoading] = useState(false);
    const [showLimitModal, setShowLimitModal] = useState(false);
    const [limitMessage, setLimitMessage] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await pacienteService.registrarPaciente(formData);
            if ("Notification" in window) {
                if (Notification.permission === "granted") {
                    new Notification("PsicoSystem Clínico", { body: "¡Expediente de paciente creado con éxito!", icon: "/favicon.ico" });
                } else if (Notification.permission !== "denied") {
                    Notification.requestPermission().then(permission => {
                        if (permission === "granted") {
                            new Notification("PsicoSystem Clínico", { body: "¡Expediente de paciente creado con éxito!", icon: "/favicon.ico" });
                        }
                    });
                }
            }
            alert("¡Paciente guardado exitosamente!");
            navigate('/dashboard');
        } catch (error) {
            const errorData = error.response?.data;
            const errorStr = typeof errorData === 'string'
                ? errorData
                : (Array.isArray(errorData) ? errorData[0] : (errorData?.detail || JSON.stringify(errorData || error.message)));

            if (errorStr && (errorStr.includes("Límite excedido") || errorStr.includes("limite") || errorStr.includes("excedido"))) {
                setLimitMessage(errorStr);
                setShowLimitModal(true);
            } else {
                alert("Error al registrar paciente: " + errorStr);
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.pageBackground}>
            <div style={styles.card}>
                <button onClick={() => navigate('/dashboard')} style={styles.backButton}>
                    <span>←</span> Volver al panel
                </button>

                <h2 style={styles.title}>Nuevo Paciente</h2>
                <p style={styles.subtitle}>Expediente clínico (CU-02)</p>
                
                <form onSubmit={handleSubmit}>
                    {['Nombre Completo', 'Cédula de Identidad (CI)', 'Fecha de Nacimiento', 'Teléfono'].map((label, idx) => {
                        const fields = ['nombre', 'ci', 'fecha_nacimiento', 'telefono'];
                        const types = ['text', 'text', 'date', 'tel'];
                        return (
                            <div key={fields[idx]} style={styles.inputGroup}>
                                <label style={styles.label}>{label}</label>
                                <input 
                                    type={types[idx]}
                                    style={styles.input}
                                    onChange={e => setFormData({...formData, [fields[idx]]: e.target.value})} 
                                    required 
                                />
                            </div>
                        );
                    })}
                    <button type="submit" style={styles.submitButton} disabled={loading}>
                        {loading ? 'Guardando...' : 'Registrar Paciente'}
                    </button>
                </form>
            </div>

            {/* Modal de Límite de Suscripción Excedido (Incentivo de Venta SaaS) */}
            {showLimitModal && (
                <div style={modalStyles.limitModalOverlay}>
                    <div style={modalStyles.limitModalContent}>
                        <div style={modalStyles.limitIconContainer}>
                            <span style={{ fontSize: '48px' }}>👑</span>
                        </div>
                        <h3 style={modalStyles.limitModalTitle}>¡Límite de Plan Alcanzado!</h3>
                        <p style={modalStyles.limitModalText}>{limitMessage}</p>
                        <div style={modalStyles.limitIncentiveCard}>
                            <p style={{ margin: 0, fontWeight: 'bold', color: '#1e293b' }}>
                                ¡Haz crecer tu clínica hoy!
                            </p>
                            <p style={{ margin: '4px 0 0 0', color: '#64748b' }}>
                                Actualiza a un plan superior para registrar pacientes y psicólogos sin restricciones.
                            </p>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '25px', width: '100%' }}>
                            <button 
                                onClick={() => {
                                    setShowLimitModal(false);
                                    navigate('/suscripcion');
                                }}
                                style={modalStyles.limitBtnUpgrade}
                            >
                                🚀 ACTUALIZAR PLAN AHORA
                            </button>
                            <button 
                                onClick={() => setShowLimitModal(false)}
                                style={modalStyles.limitBtnCancel}
                            >
                                Mantener plan actual
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

const modalStyles = {
    limitModalOverlay: {
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        backgroundColor: 'rgba(15, 23, 42, 0.65)',
        backdropFilter: 'blur(8px)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 2000
    },
    limitModalContent: {
        backgroundColor: 'white',
        padding: '35px',
        borderRadius: '20px',
        width: '100%',
        maxWidth: '420px',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
        border: '1px solid #e2e8f0',
        fontFamily: '"Inter", sans-serif'
    },
    limitIconContainer: {
        width: '80px',
        height: '80px',
        borderRadius: '50%',
        backgroundColor: '#fef3c7',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: '20px'
    },
    limitModalTitle: {
        margin: '0 0 10px 0',
        fontSize: '20px',
        fontWeight: '900',
        color: '#0f172a'
    },
    limitModalText: {
        fontSize: '13.5px',
        color: '#ef4444',
        margin: '0 0 20px 0',
        fontWeight: '600',
        lineHeight: '1.5',
        backgroundColor: '#fef2f2',
        padding: '10px 15px',
        borderRadius: '8px',
        border: '1px solid #fecaca'
    },
    limitIncentiveCard: {
        backgroundColor: '#f8fafc',
        padding: '15px',
        borderRadius: '10px',
        border: '1px solid #cbd5e1',
        fontSize: '12px',
        lineHeight: '1.5',
        textAlign: 'center'
    },
    limitBtnUpgrade: {
        width: '100%',
        padding: '14px',
        backgroundColor: '#2563eb',
        color: 'white',
        border: 'none',
        borderRadius: '8px',
        fontWeight: 'bold',
        cursor: 'pointer',
        fontSize: '13px',
        boxShadow: '0 4px 6px -1px rgba(37, 99, 235, 0.2)',
        marginTop: '15px'
    },
    limitBtnCancel: {
        width: '100%',
        padding: '12px',
        backgroundColor: 'transparent',
        color: '#64748b',
        border: 'none',
        borderRadius: '8px',
        fontWeight: '600',
        cursor: 'pointer',
        fontSize: '12px'
    }
};

export default RegistroPaciente;