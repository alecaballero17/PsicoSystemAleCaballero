// [SPRINT 1 - T019] Flujo de Recuperación: Interfaz de restablecimiento de credenciales.
// [CU-03] Recuperación de Credenciales: Solicitud vía email y confirmación con token.
// [RNF-03] Seguridad: El endpoint no revela si el email existe (anti-enumeración).
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/axiosConfig';

// ============================================================
// PASO 1: Formulario de solicitud de recuperación por email
// ============================================================
const PasoSolicitud = ({ onExito }) => {
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [mensaje, setMensaje] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMensaje('');
        try {
            // [SPRINT 1 - T019] [T020] POST al endpoint SMTP de recuperación
            await apiClient.post('auth/password-reset/', { email });
            // [RNF-03] No se revela si existe o no: siempre mostramos el mismo mensaje
            setMensaje('Si el correo existe en el sistema, recibirás las instrucciones en breve.');
            onExito(email);
        } catch {
            setMensaje('Error de conexión. Verifica tu red e inténtalo de nuevo.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <h2 style={styles.title}>Recuperar Acceso</h2>
            <p style={styles.subtitle}>Ingresa el correo registrado en el sistema</p>

            {mensaje && <div style={styles.infoBox}>{mensaje}</div>}

            <form onSubmit={handleSubmit}>
                <div style={styles.inputGroup}>
                    <label style={styles.label}>Correo Electrónico</label>
                    <input
                        type="email"
                        style={styles.input}
                        value={email}
                        onChange={e => setEmail(e.target.value)}
                        placeholder="usuario@clinica.com"
                        required
                    />
                </div>
                <button type="submit" disabled={loading} style={styles.button}>
                    {loading ? 'Enviando...' : 'Enviar Instrucciones'}
                </button>
            </form>
        </>
    );
};

// ============================================================
// PASO 2: Formulario de confirmación (uid + token + nueva pass)
// ============================================================
const PasoConfirmacion = ({ email }) => {
    const navigate = useNavigate();
    const [form, setForm] = useState({ uid: '', token: '', new_password: '', confirmar: '' });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [exito, setExito] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (form.new_password !== form.confirmar) {
            setError('Las contraseñas no coinciden.');
            return;
        }
        if (form.new_password.length < 8) {
            setError('La contraseña debe tener al menos 8 caracteres.');
            return;
        }

        setLoading(true);
        try {
            // [SPRINT 1 - T019] POST al endpoint de confirmación con uid, token y nueva contraseña
            await apiClient.post('auth/password-reset/confirm/', {
                uid: form.uid,
                token: form.token,
                new_password: form.new_password,
            });
            setExito(true);
        } catch (err) {
            const msg = err.response?.data?.error || 'Token inválido o expirado. Solicita un nuevo enlace.';
            setError(msg);
        } finally {
            setLoading(false);
        }
    };

    if (exito) {
        return (
            <div style={{ textAlign: 'center' }}>
                <div style={styles.successIcon}>✅</div>
                <h2 style={styles.title}>¡Contraseña Restablecida!</h2>
                <p style={styles.subtitle}>Tu acceso ha sido reconfigurado correctamente.</p>
                <button onClick={() => navigate('/')} style={styles.button}>
                    Volver al Login
                </button>
            </div>
        );
    }

    return (
        <>
            <h2 style={styles.title}>Nueva Contraseña</h2>
            <p style={styles.subtitle}>
                Revisa el correo de <strong>{email}</strong> y copia los datos del enlace.
            </p>

            {error && <div style={styles.errorBox}>{error}</div>}

            <form onSubmit={handleSubmit}>
                {[
                    { key: 'uid', label: 'UID del enlace', type: 'text', ph: 'Ej: MTI=' },
                    { key: 'token', label: 'Token del enlace', type: 'text', ph: 'abc123-...' },
                    { key: 'new_password', label: 'Nueva Contraseña', type: 'password', ph: 'Mínimo 8 caracteres' },
                    { key: 'confirmar', label: 'Confirmar Contraseña', type: 'password', ph: 'Repite la contraseña' },
                ].map(({ key, label, type, ph }) => (
                    <div key={key} style={styles.inputGroup}>
                        <label style={styles.label}>{label}</label>
                        <input
                            type={type}
                            style={styles.input}
                            placeholder={ph}
                            value={form[key]}
                            onChange={e => setForm({ ...form, [key]: e.target.value })}
                            required
                        />
                    </div>
                ))}
                <button type="submit" disabled={loading} style={styles.button}>
                    {loading ? 'Procesando...' : 'Restablecer Contraseña'}
                </button>
            </form>
        </>
    );
};

// ============================================================
// COMPONENTE RAÍZ: Orquesta los 2 pasos del flujo CU-03
// ============================================================
const RecuperarContrasena = () => {
    const navigate = useNavigate();
    const [paso, setPaso] = useState(1);
    const [emailUsado, setEmailUsado] = useState('');

    const handleSolicitudExitosa = (email) => {
        setEmailUsado(email);
        setPaso(2);
    };

    return (
        <div style={styles.pageBackground}>
            <div style={styles.card}>
                {/* Indicador de pasos */}
                <div style={styles.stepsBar}>
                    <div style={{ ...styles.step, ...(paso === 1 ? styles.stepActive : styles.stepDone) }}>
                        1. Solicitar
                    </div>
                    <div style={styles.stepDivider}>›</div>
                    <div style={{ ...styles.step, ...(paso === 2 ? styles.stepActive : {}) }}>
                        2. Confirmar
                    </div>
                </div>

                <div style={styles.content}>
                    {paso === 1
                        ? <PasoSolicitud onExito={handleSolicitudExitosa} />
                        : <PasoConfirmacion email={emailUsado} />
                    }
                </div>

                <div style={styles.footer}>
                    <button onClick={() => navigate('/')} style={styles.linkBtn}>
                        ← Volver al inicio de sesión
                    </button>
                </div>
            </div>
        </div>
    );
};

// ============================================================
// ESTILOS (inline, consistentes con el sistema de diseño)
// ============================================================
const styles = {
    pageBackground: {
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
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
        overflow: 'hidden',
    },
    stepsBar: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '16px 20px',
        backgroundColor: '#f8fafc',
        borderBottom: '1px solid #e2e8f0',
        gap: '8px',
    },
    step: {
        fontSize: '12px',
        fontWeight: '600',
        color: '#94a3b8',
        padding: '4px 10px',
        borderRadius: '20px',
    },
    stepActive: {
        color: '#2563eb',
        backgroundColor: '#eff6ff',
    },
    stepDone: {
        color: '#16a34a',
        backgroundColor: '#f0fdf4',
    },
    stepDivider: {
        color: '#cbd5e1',
        fontSize: '16px',
    },
    content: {
        padding: '30px',
    },
    title: {
        margin: '0 0 6px 0',
        fontSize: '20px',
        fontWeight: '800',
        color: '#0f172a',
    },
    subtitle: {
        margin: '0 0 24px 0',
        fontSize: '13px',
        color: '#64748b',
    },
    inputGroup: {
        marginBottom: '18px',
    },
    label: {
        display: 'block',
        fontSize: '11px',
        fontWeight: '700',
        color: '#475569',
        marginBottom: '6px',
        textTransform: 'uppercase',
        letterSpacing: '0.5px',
    },
    input: {
        width: '100%',
        padding: '11px 14px',
        borderRadius: '8px',
        border: '1px solid #cbd5e1',
        fontSize: '14px',
        boxSizing: 'border-box',
        outline: 'none',
        transition: 'border-color 0.2s',
    },
    button: {
        width: '100%',
        padding: '13px',
        backgroundColor: '#2563eb',
        color: 'white',
        border: 'none',
        borderRadius: '8px',
        fontSize: '14px',
        fontWeight: '700',
        cursor: 'pointer',
        marginTop: '6px',
        letterSpacing: '0.3px',
    },
    infoBox: {
        padding: '12px 14px',
        borderRadius: '8px',
        backgroundColor: '#eff6ff',
        border: '1px solid #bfdbfe',
        color: '#1d4ed8',
        fontSize: '13px',
        marginBottom: '20px',
        lineHeight: '1.5',
    },
    errorBox: {
        padding: '12px 14px',
        borderRadius: '8px',
        backgroundColor: '#fef2f2',
        border: '1px solid #fecaca',
        color: '#b91c1c',
        fontSize: '13px',
        marginBottom: '20px',
    },
    footer: {
        padding: '16px 30px',
        borderTop: '1px solid #f1f5f9',
        textAlign: 'center',
    },
    linkBtn: {
        background: 'none',
        border: 'none',
        color: '#64748b',
        fontSize: '13px',
        cursor: 'pointer',
        textDecoration: 'underline',
    },
    successIcon: {
        fontSize: '48px',
        marginBottom: '12px',
    },
};

export default RecuperarContrasena;
