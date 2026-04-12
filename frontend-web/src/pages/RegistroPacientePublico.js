// [SPRINT 1 - T015] Flujo de Autogestión de credenciales por el Paciente.
// [SPRINT 1 - RF-29] Vinculación inicial de Tenant en el registro público.
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/axiosConfig';

export const RegistroPacientePublico = () => {
    const navigate = useNavigate();
    const [clinicas, setClinicas] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [formData, setFormData] = useState({
        clinica_id: '',
        nombre: '',
        ci: '',
        email: '',
        password: '',
    });

    // Obtener lista de clínicas activas (RF-29 Dropdown)
    useEffect(() => {
        const fetchClinicas = async () => {
            try {
                // Endpoint público creado en Sprint 1 - T015
                const res = await apiClient.get('clinicas/');
                setClinicas(res.data);
            } catch (err) {
                console.error("Error al obtener clínicas", err);
            }
        };
        fetchClinicas();
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        if (!formData.clinica_id) {
            setError('Debes seleccionar una clínica.');
            setLoading(false);
            return;
        }

        try {
            await apiClient.post('pacientes/registro-publico/', formData);
            alert("¡Registro completado! Ahora puedes iniciar sesión.");
            navigate('/');
        } catch (err) {
            const apiErrors = err.response?.data;
            if (apiErrors) {
                // Formatting DRF errors as string
                const errorMsg = Object.values(apiErrors).flat().join(' ');
                setError(errorMsg || 'Error durante el registro.');
            } else {
                setError('Error de conexión. Intente nuevamente.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.container}>
            <div style={styles.card}>
                <div style={styles.logoIcon}>⚕️</div>
                <h1 style={styles.title}>Registro de Paciente</h1>
                <p style={styles.subtitle}>Crea tu cuenta de autogestión</p>

                {error && <div style={styles.errorBox}>{error}</div>}

                <form onSubmit={handleSubmit}>
                    <div style={styles.inputGroup}>
                        <label style={styles.label}>Clínica u Hospital</label>
                        <select
                            name="clinica_id"
                            value={formData.clinica_id}
                            onChange={handleChange}
                            style={styles.input}
                            required
                        >
                            <option value="">-- Selecciona tu centro médico --</option>
                            {clinicas.map((cl) => (
                                <option key={cl.id} value={cl.id}>{cl.nombre}</option>
                            ))}
                        </select>
                    </div>

                    <div style={styles.inputGroup}>
                        <label style={styles.label}>Nombre Completo</label>
                        <input
                            type="text"
                            name="nombre"
                            value={formData.nombre}
                            onChange={handleChange}
                            style={styles.input}
                            required
                        />
                    </div>

                    <div style={styles.inputGroup}>
                        <label style={styles.label}>Cédula de Identidad</label>
                        <input
                            type="text"
                            name="ci"
                            value={formData.ci}
                            onChange={handleChange}
                            style={styles.input}
                            required
                        />
                    </div>

                    <div style={styles.inputGroup}>
                        <label style={styles.label}>Correo Electrónico (Usuario)</label>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            style={styles.input}
                            required
                        />
                    </div>

                    <div style={styles.inputGroup}>
                        <label style={styles.label}>Contraseña</label>
                        <input
                            type="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            style={styles.input}
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        style={{
                            ...styles.button,
                            backgroundColor: loading ? '#94a3b8' : '#2563eb'
                        }}
                    >
                        {loading ? 'Procesando...' : 'Completar Registro'}
                    </button>

                    <div style={{ textAlign: 'center', marginTop: '16px' }}>
                        <button
                            type="button"
                            onClick={() => navigate('/')}
                            style={styles.link}
                        >
                            ¿Ya tienes cuenta? Inicia sesión
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

// ===============================================
// ESTILOS (Alineados con el Login)
// ===============================================
const styles = {
    container: {
        minHeight: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#0f172a',
        padding: '20px',
    },
    card: {
        width: '100%',
        maxWidth: '460px',
        backgroundColor: 'white',
        borderRadius: '14px',
        padding: '30px',
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
    },
    title: {
        margin: '0 0 6px 0',
        fontSize: '24px',
        fontWeight: '800',
        color: '#0f172a',
        textAlign: 'center',
    },
    subtitle: {
        margin: '0 0 24px 0',
        fontSize: '14px',
        color: '#64748b',
        textAlign: 'center',
    },
    logoIcon: {
        fontSize: '48px',
        textAlign: 'center',
        marginBottom: '10px',
    },
    inputGroup: {
        marginBottom: '16px',
    },
    label: {
        display: 'block',
        fontSize: '12px',
        fontWeight: '700',
        color: '#475569',
        marginBottom: '6px',
        textTransform: 'uppercase',
    },
    input: {
        width: '100%',
        padding: '12px',
        borderRadius: '8px',
        border: '1px solid #cbd5e1',
        fontSize: '14px',
        boxSizing: 'border-box',
    },
    button: {
        width: '100%',
        padding: '14px',
        color: 'white',
        border: 'none',
        borderRadius: '8px',
        fontSize: '14px',
        fontWeight: '700',
        cursor: 'pointer',
        marginTop: '10px',
    },
    link: {
        background: 'none',
        border: 'none',
        color: '#2563eb',
        fontSize: '13px',
        cursor: 'pointer',
        textDecoration: 'underline',
    },
    errorBox: {
        padding: '12px',
        borderRadius: '8px',
        backgroundColor: '#fef2f2',
        border: '1px solid #fecaca',
        color: '#b91c1c',
        fontSize: '13px',
        marginBottom: '20px',
        textAlign: 'center',
    },
};

export default RegistroPacientePublico;
