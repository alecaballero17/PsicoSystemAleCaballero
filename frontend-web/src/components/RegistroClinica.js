import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const RegistroClinica = () => {
    const [formData, setFormData] = useState({
        nombre: '',
        nit: '',
        direccion: '',
        telefono: '',
        email_contacto: ''
    });
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('userToken');
        
        try {
            // RF-29: Petición para crear la instancia de Clínica (Tenant)
            await axios.post('http://127.0.0.1:8000/api/clinicas/', formData, {
                headers: { 
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            alert("INSTANCIA DE CLÍNICA ESTABLECIDA CORRECTAMENTE");
            navigate('/dashboard');
        } catch (error) {
            console.error("Error en RF-29:", error);
            alert("ERROR DE AUTORIZACIÓN: Solo el Administrador de Sistema puede registrar nuevas clínicas.");
        }
    };

    return (
        <div style={styles.layout}>
            <div style={styles.card}>
                <header style={styles.cardHeader}>
                    <h2 style={styles.title}>REGISTRO DE UNIDAD CLÍNICA</h2>
                    <p style={styles.subtitle}>Configuración de Tenant ID - Módulo Administrativo</p>
                </header>

                <form onSubmit={handleSubmit} style={styles.form}>
                    <div style={styles.inputGroup}>
                        <label style={styles.label}>RAZÓN SOCIAL / NOMBRE</label>
                        <input 
                            type="text" 
                            style={styles.input} 
                            placeholder="Ej. Centro Psicológico Santa Cruz"
                            onChange={(e) => setFormData({...formData, nombre: e.target.value})}
                            required 
                        />
                    </div>

                    <div style={styles.grid}>
                        <div style={styles.inputGroup}>
                            <label style={styles.label}>NIT / IDENTIFICADOR</label>
                            <input 
                                type="text" 
                                style={styles.input} 
                                placeholder="12345678"
                                onChange={(e) => setFormData({...formData, nit: e.target.value})}
                                required 
                            />
                        </div>
                        <div style={styles.inputGroup}>
                            <label style={styles.label}>TELÉFONO DE CONTACTO</label>
                            <input 
                                type="text" 
                                style={styles.input} 
                                placeholder="+591 ..."
                                onChange={(e) => setFormData({...formData, telefono: e.target.value})}
                                required 
                            />
                        </div>
                    </div>

                    <div style={styles.inputGroup}>
                        <label style={styles.label}>DIRECCIÓN FÍSICA ESTRATÉGICA</label>
                        <input 
                            type="text" 
                            style={styles.input} 
                            placeholder="Av. Las Américas #123"
                            onChange={(e) => setFormData({...formData, direccion: e.target.value})}
                            required 
                        />
                    </div>

                    <div style={styles.actions}>
                        <button type="button" onClick={() => navigate('/dashboard')} style={styles.btnSecondary}>
                            CANCELAR
                        </button>
                        <button type="submit" style={styles.btnPrimary}>
                            CONFIRMAR ALTA (RF-29)
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

const styles = {
    layout: { height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', backgroundColor: '#f1f5f9' },
    card: { width: '500px', backgroundColor: 'white', borderRadius: '12px', boxShadow: '0 10px 25px rgba(0,0,0,0.05)', border: '1px solid #e2e8f0', overflow: 'hidden' },
    cardHeader: { padding: '30px', borderBottom: '1px solid #f1f5f9', textAlign: 'center', backgroundColor: '#0f172a' },
    title: { margin: 0, color: 'white', fontSize: '18px', fontWeight: '800', letterSpacing: '0.5px' },
    subtitle: { margin: '5px 0 0 0', color: '#94a3b8', fontSize: '11px', fontWeight: '600' },
    form: { padding: '30px' },
    inputGroup: { marginBottom: '20px' },
    grid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' },
    label: { display: 'block', fontSize: '11px', fontWeight: 'bold', color: '#64748b', marginBottom: '8px', textTransform: 'uppercase' },
    input: { width: '100%', padding: '12px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '14px', boxSizing: 'border-box', outline: 'none' },
    actions: { display: 'flex', gap: '15px', marginTop: '10px' },
    btnPrimary: { flex: 2, padding: '14px', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', fontSize: '13px' },
    btnSecondary: { flex: 1, padding: '14px', backgroundColor: 'white', color: '#64748b', border: '1px solid #cbd5e1', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', fontSize: '13px' }
};

export default RegistroClinica;