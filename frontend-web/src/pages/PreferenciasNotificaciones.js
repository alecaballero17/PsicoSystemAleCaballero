import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/axiosConfig';

const PreferenciasNotificaciones = () => {
    const navigate = useNavigate();
    const [prefs, setPrefs] = useState({
        email_notif_citas: true,
        email_notif_reportes: true,
        push_notif_alertas: true
    });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState(null);
    const [error, setError] = useState(null);
    const [pushPermission, setPushPermission] = useState(
        "Notification" in window ? Notification.permission : "default"
    );

    useEffect(() => {
        const fetchPreferences = async () => {
            try {
                const response = await apiClient.get('auth/me/');
                setPrefs({
                    email_notif_citas: response.data.email_notif_citas ?? true,
                    email_notif_reportes: response.data.email_notif_reportes ?? true,
                    push_notif_alertas: response.data.push_notif_alertas ?? true
                });
            } catch (err) {
                console.error("Error cargando preferencias de usuario", err);
                setError("No se pudieron cargar las preferencias de notificación.");
            } finally {
                setLoading(false);
            }
        };
        fetchPreferences();
    }, []);

    const handleToggle = (key) => {
        setPrefs(prev => ({
            ...prev,
            [key]: !prev[key]
        }));
    };

    const requestPushPermission = async () => {
        if (!("Notification" in window)) {
            alert("Este navegador no soporta notificaciones de escritorio.");
            return;
        }

        const permission = await Notification.requestPermission();
        setPushPermission(permission);

        if (permission === "granted") {
            new Notification("PsicoSystem Notificaciones", {
                body: "¡Notificaciones push activadas correctamente!",
                icon: "/favicon.ico"
            });
        }
    };

    const testNotification = () => {
        if (!("Notification" in window)) return;
        if (Notification.permission === "granted") {
            new Notification("Prueba de Notificación", {
                body: "Esta es una notificación de prueba del portal PsicoSystem.",
                icon: "/favicon.ico"
            });
        } else {
            alert("Por favor, active primero las notificaciones de navegador.");
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        setMessage(null);
        setError(null);

        try {
            await apiClient.put('auth/me/', prefs);
            setMessage("Preferencias de notificación guardadas exitosamente.");
            setTimeout(() => setMessage(null), 3000);
        } catch (err) {
            console.error("Error guardando preferencias", err);
            setError("Error al guardar las preferencias de notificación.");
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <div style={styles.layout}>
                <div style={styles.card}>
                    <div style={{ padding: '40px', textAlign: 'center', color: '#64748b' }}>
                        Cargando preferencias de notificación...
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div style={styles.layout}>
            <div style={styles.card}>
                <header style={styles.cardHeader}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                        <button onClick={() => navigate('/dashboard')} style={styles.btnBack}>← Volver</button>
                        <h2 style={styles.title}>PREFERENCIAS DE NOTIFICACIÓN (CU22)</h2>
                        <div style={{ width: '60px' }}></div>
                    </div>
                    <p style={styles.subtitle}>Configuración de canales y alertas automáticas</p>
                </header>

                <form onSubmit={handleSubmit} style={styles.form}>
                    {error && <div style={styles.errorBox}>{error}</div>}
                    {message && <div style={styles.successBox}>{message}</div>}

                    <div style={styles.section}>
                        <h3 style={styles.sectionTitle}>✉️ Canales por Correo Electrónico</h3>
                        <p style={styles.sectionDesc}>Configura qué notificaciones deseas recibir en tu dirección de correo electrónico institucional.</p>
                        
                        <div style={styles.preferenceRow} onClick={() => handleToggle('email_notif_citas')}>
                            <div style={styles.prefInfo}>
                                <span style={styles.prefLabel}>Agendamiento y Cancelación de Citas</span>
                                <span style={styles.prefSub}>Recibe un correo cada vez que se programe, mueva o cancele una sesión médica.</span>
                            </div>
                            <div style={prefs.email_notif_citas ? styles.switchOn : styles.switchOff}>
                                <div style={prefs.email_notif_citas ? styles.switchKnobOn : styles.switchKnobOff}></div>
                            </div>
                        </div>

                        <div style={styles.preferenceRow} onClick={() => handleToggle('email_notif_reportes')}>
                            <div style={styles.prefInfo}>
                                <span style={styles.prefLabel}>Reportes Clínicos y Sistema</span>
                                <span style={styles.prefSub}>Recibe resúmenes de métricas mensuales y notificaciones de auditorías generales.</span>
                            </div>
                            <div style={prefs.email_notif_reportes ? styles.switchOn : styles.switchOff}>
                                <div style={prefs.email_notif_reportes ? styles.switchKnobOn : styles.switchKnobOff}></div>
                            </div>
                        </div>
                    </div>

                    <div style={styles.section}>
                        <h3 style={styles.sectionTitle}>🔔 Notificaciones en Tiempo Real (Navegador)</h3>
                        <p style={styles.sectionDesc}>Configura alertas instantáneas en tu ordenador cuando estés navegando en el portal.</p>

                        <div style={styles.preferenceRow} onClick={() => handleToggle('push_notif_alertas')}>
                            <div style={styles.prefInfo}>
                                <span style={styles.prefLabel}>Alertas de Diagnósticos de IA</span>
                                <span style={styles.prefSub}>Te notifica inmediatamente cuando la IA de Gemini termine de analizar síntomas clínicos.</span>
                            </div>
                            <div style={prefs.push_notif_alertas ? styles.switchOn : styles.switchOff}>
                                <div style={prefs.push_notif_alertas ? styles.switchKnobOn : styles.switchKnobOff}></div>
                            </div>
                        </div>

                        <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
                            {pushPermission !== "granted" ? (
                                <button 
                                    type="button" 
                                    onClick={requestPushPermission} 
                                    style={styles.btnAction}
                                >
                                    Solicitar Permiso Push 🔔
                                </button>
                            ) : (
                                <button 
                                    type="button" 
                                    onClick={testNotification} 
                                    style={styles.btnActionSecondary}
                                >
                                    Probar Notificación de Navegador 🖥️
                                </button>
                            )}
                        </div>
                    </div>

                    <div style={styles.actions}>
                        <button type="submit" style={styles.btnPrimary} disabled={saving}>
                            {saving ? 'GUARDANDO PREFERENCIAS...' : 'GUARDAR PREFERENCIAS'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

const styles = {
    layout: { padding: '40px 0', display: 'flex', justifyContent: 'center', alignItems: 'center', backgroundColor: '#f1f5f9', minHeight: 'calc(100vh - 64px)' },
    card: { width: '600px', backgroundColor: 'white', borderRadius: '16px', boxShadow: '0 10px 25px rgba(0,0,0,0.05)', border: '1px solid #e2e8f0', overflow: 'hidden' },
    cardHeader: { padding: '25px', borderBottom: '1px solid #f1f5f9', textAlign: 'center', backgroundColor: '#0f172a' },
    title: { margin: 0, color: 'white', fontSize: '18px', fontWeight: '800', letterSpacing: '0.5px' },
    subtitle: { margin: '5px 0 0 0', color: '#94a3b8', fontSize: '11px', fontWeight: '600' },
    form: { padding: '30px' },
    section: { marginBottom: '30px', paddingBottom: '20px', borderBottom: '1px solid #f1f5f9' },
    sectionTitle: { fontSize: '14px', color: '#0f172a', marginBottom: '6px', marginTop: '0', fontWeight: 'bold' },
    sectionDesc: { fontSize: '12px', color: '#64748b', margin: '0 0 20px 0' },
    preferenceRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '15px', borderRadius: '8px', border: '1px solid #f1f5f9', cursor: 'pointer', transition: 'background-color 0.2s', marginBottom: '12px', ':hover': { backgroundColor: '#f8fafc' } },
    prefInfo: { display: 'flex', flexDirection: 'column', flex: 1, paddingRight: '20px' },
    prefLabel: { fontSize: '13px', fontWeight: 'bold', color: '#1e293b' },
    prefSub: { fontSize: '11px', color: '#64748b', marginTop: '4px' },
    
    // Switch styles
    switchOn: { width: '46px', height: '24px', backgroundColor: '#10b981', borderRadius: '12px', position: 'relative', transition: 'all 0.2s' },
    switchOff: { width: '46px', height: '24px', backgroundColor: '#cbd5e1', borderRadius: '12px', position: 'relative', transition: 'all 0.2s' },
    switchKnobOn: { width: '18px', height: '18px', backgroundColor: 'white', borderRadius: '50%', position: 'absolute', top: '3px', right: '3px', transition: 'all 0.2s' },
    switchKnobOff: { width: '18px', height: '18px', backgroundColor: 'white', borderRadius: '50%', position: 'absolute', top: '3px', left: '3px', transition: 'all 0.2s' },

    errorBox: { padding: '12px', backgroundColor: '#fef2f2', color: '#b91c1c', border: '1px solid #fecaca', borderRadius: '6px', marginBottom: '20px', fontSize: '13px' },
    successBox: { padding: '12px', backgroundColor: '#f0fdf4', color: '#15803d', border: '1px solid #bbf7d0', borderRadius: '6px', marginBottom: '20px', fontSize: '13px' },
    actions: { display: 'flex', justifyContent: 'flex-end', marginTop: '30px' },
    btnPrimary: { width: '100%', padding: '14px', backgroundColor: '#0f172a', color: 'white', border: 'none', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', fontSize: '13px' },
    btnBack: { backgroundColor: 'transparent', color: '#94a3b8', border: '1px solid #334155', padding: '5px 10px', borderRadius: '4px', fontSize: '12px', cursor: 'pointer', fontWeight: 'bold' },
    btnAction: { padding: '10px 16px', backgroundColor: '#2563eb', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', fontSize: '12px' },
    btnActionSecondary: { padding: '10px 16px', backgroundColor: '#f1f5f9', color: '#475569', border: '1px solid #cbd5e1', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', fontSize: '12px' }
};

export default PreferenciasNotificaciones;
