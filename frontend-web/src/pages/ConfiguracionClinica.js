// [ALINEACIÓN T024] - Gestión de identidad organizacional y persistencia de datos del Tenant (RF-29).
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import apiClient from '../api/axiosConfig';

const ConfiguracionClinica = () => {
    const navigate = useNavigate();
    const { updateTenant } = useAuth();
    const [formData, setFormData] = useState({
        nombre: '',
        nit: '',
        direccion: '',
        telefono: '',
        email_contacto: '',
        logo_url: ''
    });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState(null);
    const [error, setError] = useState(null);

    // Carga Automática de Datos (GET)
    useEffect(() => {
        const fetchClinica = async () => {
            try {
                const response = await apiClient.get('clinica/me/');
                setFormData({
                    nombre: response.data.nombre || '',
                    nit: response.data.nit || '',
                    direccion: response.data.direccion || '',
                    telefono: response.data.telefono || '',
                    email_contacto: response.data.email_contacto || '',
                    logo_url: response.data.logo_url || ''
                });
            } catch (err) {
                console.error("Error cargando configuración de clínica", err);
                setError("No se pudo cargar la información de la clínica.");
            } finally {
                setLoading(false);
            }
        };
        fetchClinica();
    }, []);

    // Actualización de Datos (PUT)
    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        setMessage(null);
        setError(null);

        try {
            await apiClient.put('clinica/me/', formData);
            updateTenant(formData); // [ALINEACIÓN RF-29] Sincronización en tiempo real
            setMessage("Configuración guardada exitosamente.");
        } catch (err) {
            console.error("Error guardando clínica", err);
            if (err.response?.data?.nit) {
                setError("El NIT proporcionado ya está en uso por otra clínica.");
            } else {
                setError("Error al guardar la configuración.");
            }
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <div style={styles.layout}>
                <div style={styles.card}>
                    <div style={{ padding: '40px', textAlign: 'center', color: '#64748b' }}>
                        Cargando configuración institucional...
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div style={styles.layout}>
            <div style={styles.card}>
                <header style={styles.cardHeader}>
                    <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px'}}>
                        <button onClick={() => navigate('/dashboard')} style={styles.btnBack}>← Volver</button>
                        <h2 style={styles.title}>CONFIGURACIÓN INSTITUCIONAL</h2>
                        <div style={{width: '60px'}}></div> {/* Spacer balance */}
                    </div>
                    <p style={styles.subtitle}>Mantenimiento del Perfil de la Clínica (Tenant)</p>
                </header>

                <form onSubmit={handleSubmit} style={styles.form}>
                    {error && <div style={styles.errorBox}>{error}</div>}
                    {message && <div style={styles.successBox}>{message}</div>}

                    <h3 style={styles.sectionTitle}>Datos de la Compañía</h3>
                    
                    <div style={styles.inputGroup}>
                        <label style={styles.label}>RAZÓN SOCIAL / NOMBRE</label>
                        <input 
                            type="text" 
                            style={styles.input} 
                            value={formData.nombre} 
                            onChange={(e) => setFormData({...formData, nombre: e.target.value})} 
                            required 
                        />
                    </div>

                    <div style={styles.grid}>
                        <div style={styles.inputGroup}>
                            <label style={styles.label}>NIT / RUT</label>
                            <input 
                                type="text" 
                                style={styles.input} 
                                value={formData.nit} 
                                onChange={(e) => setFormData({...formData, nit: e.target.value})} 
                                required 
                            />
                        </div>
                        <div style={styles.inputGroup}>
                            <label style={styles.label}>TELÉFONO DE CONTACTO</label>
                            <input 
                                type="text" 
                                style={styles.input} 
                                value={formData.telefono} 
                                onChange={(e) => setFormData({...formData, telefono: e.target.value})} 
                                required 
                            />
                        </div>
                    </div>

                    <div style={styles.inputGroup}>
                        <label style={styles.label}>EMAIL CORPORATIVO</label>
                        <input 
                            type="email" 
                            style={styles.input} 
                            value={formData.email_contacto} 
                            onChange={(e) => setFormData({...formData, email_contacto: e.target.value})} 
                            required 
                        />
                    </div>

                    <div style={styles.inputGroup}>
                        <label style={styles.label}>DIRECCIÓN FÍSICA / LEGAL</label>
                        <input 
                            type="text" 
                            style={styles.input} 
                            value={formData.direccion} 
                            onChange={(e) => setFormData({...formData, direccion: e.target.value})} 
                            required 
                        />
                    </div>

                    <div style={styles.inputGroup}>
                        <label style={styles.label}>LOGO INSTITUCIONAL (URL)</label>
                        <input 
                            type="url" 
                            style={styles.input} 
                            value={formData.logo_url} 
                            onChange={(e) => setFormData({...formData, logo_url: e.target.value})} 
                            placeholder="https://ejemplo.com/logo.png"
                        />
                        <p style={styles.helpText}>URL directa a la imagen de su corporación</p>
                    </div>

                    <div style={styles.actions}>
                        <button type="submit" style={styles.btnPrimary} disabled={saving}>
                            {saving ? 'GUARDANDO...' : 'GUARDAR CAMBIOS DEL TENANT'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

const styles = {
    layout: { padding: '40px 0', display: 'flex', justifyContent: 'center', alignItems: 'center', backgroundColor: '#f1f5f9', minHeight: 'calc(100vh - 64px)' },
    card: { width: '600px', backgroundColor: 'white', borderRadius: '12px', boxShadow: '0 10px 25px rgba(0,0,0,0.05)', border: '1px solid #e2e8f0', overflow: 'hidden' },
    cardHeader: { padding: '25px', borderBottom: '1px solid #f1f5f9', textAlign: 'center', backgroundColor: '#0f172a' },
    title: { margin: 0, color: 'white', fontSize: '18px', fontWeight: '800', letterSpacing: '0.5px' },
    subtitle: { margin: '5px 0 0 0', color: '#94a3b8', fontSize: '11px', fontWeight: '600' },
    form: { padding: '30px' },
    sectionTitle: { fontSize: '14px', color: '#1e293b', marginBottom: '15px', marginTop: '0', fontWeight: 'bold' },
    inputGroup: { marginBottom: '15px' },
    grid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' },
    label: { display: 'block', fontSize: '10px', fontWeight: 'bold', color: '#64748b', marginBottom: '6px', textTransform: 'uppercase' },
    input: { width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '13px', boxSizing: 'border-box', outline: 'none' },
    helpText: { fontSize: '10px', color: '#94a3b8', margin: '4px 0 0 0' },
    errorBox: { padding: '12px', backgroundColor: '#fef2f2', color: '#b91c1c', border: '1px solid #fecaca', borderRadius: '6px', marginBottom: '20px', fontSize: '13px' },
    successBox: { padding: '12px', backgroundColor: '#f0fdf4', color: '#15803d', border: '1px solid #bbf7d0', borderRadius: '6px', marginBottom: '20px', fontSize: '13px' },
    actions: { display: 'flex', justifyContent: 'flex-end', marginTop: '30px' },
    btnPrimary: { width: '100%', padding: '14px', backgroundColor: '#0f172a', color: 'white', border: 'none', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', fontSize: '13px' },
    btnBack: { backgroundColor: 'transparent', color: '#94a3b8', border: '1px solid #334155', padding: '5px 10px', borderRadius: '4px', fontSize: '12px', cursor: 'pointer', fontWeight: 'bold' }
};

export default ConfiguracionClinica;
