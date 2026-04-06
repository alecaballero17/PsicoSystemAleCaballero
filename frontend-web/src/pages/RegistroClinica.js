import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import clinicaService from '../services/clinicaService'; 
import { useAuth } from '../context/AuthContext'; // <-- 1. IMPORTA EL HOOK AQUÍ ARRIBA

const RegistroClinica = () => {
    // 2. LLAMA AL HOOK ADENTRO DEL COMPONENTE
    const { user } = useAuth(); 
    
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
        
        // CORRECCIÓN CAUSA RAÍZ #3: Formateo estricto del payload
        const dataToSend = {
            nombre: formData.nombre,
            nit: formData.nit,
            direccion: formData.direccion,
            telefono: formData.telefono,
            email_contacto: formData.email_contacto,
            plan_suscripcion: "Basico" // Aseguramos el contrato con el Serializer
        };

        try {
            // RF-29: Petición limpia a través del servicio
            await clinicaService.registrarClinica(dataToSend);
            alert("INSTANCIA DE CLÍNICA ESTABLECIDA CORRECTAMENTE");
            navigate('/dashboard');
        } catch (error) {
            // 3. USA EL USUARIO AQUÍ ADENTRO DEL CATCH
            console.error(`Error en RF-29 provocado por Admin: ${user?.name}`, error.response?.data || error);
            alert("ERROR DE REGISTRO: Verifique los datos o sus permisos.");
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
                            value={formData.nombre}
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
                                placeholder="+591 ..."
                                value={formData.telefono}
                                onChange={(e) => setFormData({...formData, telefono: e.target.value})}
                                required 
                            />
                        </div>
                    </div>

                    {/* CAMPO: Email de Contacto */}
                    <div style={styles.inputGroup}>
                        <label style={styles.label}>EMAIL CORPORATIVO</label>
                        <input 
                            type="email" 
                            style={styles.input} 
                            placeholder="contacto@clinica.com"
                            value={formData.email_contacto}
                            onChange={(e) => setFormData({...formData, email_contacto: e.target.value})}
                            required 
                        />
                    </div>

                    <div style={styles.inputGroup}>
                        <label style={styles.label}>DIRECCIÓN FÍSICA ESTRATÉGICA</label>
                        <input 
                            type="text" 
                            style={styles.input} 
                            placeholder="Av. Las Américas #123"
                            value={formData.direccion}
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