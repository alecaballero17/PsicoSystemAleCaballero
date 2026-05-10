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
                const response = await apiClient.get('clinicas/mi/'); // Fixed URL
                setFormData({
                    nombre: response.data.nombre || '',
                    nit: response.data.nit || '',
                    direccion: response.data.direccion || '',
                    telefono: response.data.telefono || '',
                    email_contacto: response.data.email_contacto || '',
                    logo_url: response.data.logo || '' // Logo URL from backend
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

    // Manejo de archivo
    const [logoFile, setLogoFile] = useState(null);

    // Actualización de Datos (PUT)
    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        setMessage(null);
        setError(null);

        const data = new FormData();
        data.append('nombre', formData.nombre);
        data.append('nit', formData.nit);
        data.append('direccion', formData.direccion);
        data.append('telefono', formData.telefono);
        data.append('email_contacto', formData.email_contacto);
        if (logoFile) {
            data.append('logo', logoFile);
        }

        try {
            const response = await apiClient.patch('clinicas/mi/', data, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            updateTenant(response.data); 
            setFormData({ ...formData, logo_url: response.data.logo });
            setMessage("Configuración guardada exitosamente.");
        } catch (err) {
            console.error("Error guardando clínica", err);
            setError("Error al guardar la configuración institucional.");
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
                        <div style={{width: '60px'}}></div>
                    </div>
                    <p style={styles.subtitle}>Mantenimiento del Perfil de la Clínica (Tenant)</p>
                </header>

                <form onSubmit={handleSubmit} style={styles.form}>
                    {error && <div style={styles.errorBox}>{error}</div>}
                    {message && <div style={styles.successBox}>{message}</div>}

                    <div style={{ textAlign: 'center', marginBottom: '30px' }}>
                        <div style={{ 
                            width: '120px', height: '120px', borderRadius: '15px', 
                            border: '2px dashed #cbd5e1', margin: '0 auto 15px',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            overflow: 'hidden', backgroundColor: '#f8fafc'
                        }}>
                            {logoFile ? (
                                <img src={URL.createObjectURL(logoFile)} alt="Logo Preview" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                            ) : formData.logo_url ? (
                                <img src={formData.logo_url} alt="Logo" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                            ) : (
                                <span style={{ fontSize: '40px' }}>🏢</span>
                            )}
                        </div>
                        <input 
                            type="file" 
                            accept="image/*" 
                            onChange={(e) => setLogoFile(e.target.files[0])}
                            style={{ display: 'none' }}
                            id="logo-upload"
                        />
                        <label htmlFor="logo-upload" style={styles.btnSecondarySmall}>
                            📷 SUBIR / CAMBIAR LOGO
                        </label>
                    </div>

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
                        <label style={styles.label}>DIRECCIÓN FÍSICA</label>
                        <input 
                            type="text" 
                            style={styles.input} 
                            value={formData.direccion} 
                            onChange={(e) => setFormData({...formData, direccion: e.target.value})} 
                            required 
                        />
                    </div>

                    <div style={styles.actions}>
                        <button type="submit" style={styles.btnPrimary} disabled={saving}>
                            {saving ? 'GUARDANDO...' : 'GUARDAR CAMBIOS INSTITUCIONALES'}
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
    btnBack: { backgroundColor: 'transparent', color: '#94a3b8', border: '1px solid #334155', padding: '5px 10px', borderRadius: '4px', fontSize: '12px', cursor: 'pointer', fontWeight: 'bold' },
    btnSecondarySmall: { display: 'inline-block', backgroundColor: '#f1f5f9', color: '#475569', padding: '8px 16px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '11px', fontWeight: 'bold', cursor: 'pointer' }
};

export default ConfiguracionClinica;
