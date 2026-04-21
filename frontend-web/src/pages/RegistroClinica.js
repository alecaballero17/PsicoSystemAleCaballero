// [CIERRE SPRINT 1] Flujo SaaS integrado según Requerimientos 3.2 y RF-29.
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/axiosConfig'; 
import { useAuth } from '../context/AuthContext';

const RegistroClinica = () => {
    const { user } = useAuth();
    
    // ESTADOS: Agrupamos los requerimientos B2B
    const [formData, setFormData] = useState({
        // Datos de la Clínica (Tenant)
        nombre: '',
        nit: '',
        direccion: '',
        telefono: '',
        email_contacto: '',
        // Datos del SuperAdmin del Tenant
        username: '',
        password: '',
        email_admin: '',
        // Selección de Plan
        plan_id: ''
    });
    const [planes, setPlanes] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const navigate = useNavigate();

    // Consultamos los planes disponibles públicos
    useEffect(() => {
        const fetchPlanes = async () => {
            try {
                // T025: Endpoint de catálogo de planes
                const response = await apiClient.get('planes/');
                setPlanes(response.data);
            } catch (err) {
                console.error("No se pudieron cargar los planes", err);
            }
        };
        fetchPlanes();

        // [ALINEACIÓN SPRINT 1 - RF-29] Bypass: Si ya tiene clínica asignada, bloquear registro
        if (user && user.clinica_id && user.clinica_id !== "null" && user.clinica_id !== "undefined") {
            navigate('/dashboard');
        }
    }, [user, navigate]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        
        // Estructuramos el payload atómico esperado por el backend
        const atomicPayload = {
            clinica: {
                nombre: formData.nombre,
                nit: formData.nit,
                direccion: formData.direccion,
                telefono: formData.telefono,
                email_contacto: formData.email_contacto
            },
            admin: {
                username: formData.username,
                email: formData.email_admin,
                password: formData.password
            },
            plan_id: formData.plan_id
        };

            // Envío público hacia el onboarding SaaS (Alineado con backend P1)
            await apiClient.post('onboarding/', atomicPayload);
            alert("ALTA EXITOSA: La clínica, la suscripción y tu usuario administrador se crearon correctamente.");
            navigate('/login');
        } catch (err) {
            console.error("Error en alta atómica", err.response?.data || err);
            setError(err.response?.data?.detail || "No se pudo realizar el alta de la Clínica. Verifica los datos.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.layout}>
            <div style={styles.card}>
                <header style={styles.cardHeader}>
                    <h2 style={styles.title}>REGISTRO DE UNIDAD CLÍNICA</h2>
                    <p style={styles.subtitle}>Alta SaaS Corporativa (Multi-tenant) - RF-29</p>
                </header>

                <form onSubmit={handleSubmit} style={styles.form}>
                    {error && <div style={styles.errorBox}>{error}</div>}

                    {/* SECCIÓN 1: DATOS DE LA CLÍNICA */}
                    <h3 style={styles.sectionTitle}>1. Datos de la Compañía</h3>
                    <div style={styles.inputGroup}>
                        <label style={styles.label}>RAZÓN SOCIAL / NOMBRE</label>
                        <input type="text" style={styles.input} placeholder="Centro Psicológico Integral..." value={formData.nombre} onChange={(e) => setFormData({...formData, nombre: e.target.value})} required />
                    </div>

                    <div style={styles.grid}>
                        <div style={styles.inputGroup}>
                            <label style={styles.label}>NIT / RUT</label>
                            <input type="text" style={styles.input} placeholder="12345678" value={formData.nit} onChange={(e) => setFormData({...formData, nit: e.target.value})} required />
                        </div>
                        <div style={styles.inputGroup}>
                            <label style={styles.label}>TELÉFONO DE CONTACTO</label>
                            <input type="text" style={styles.input} placeholder="+591 ..." value={formData.telefono} onChange={(e) => setFormData({...formData, telefono: e.target.value})} required />
                        </div>
                    </div>

                    <div style={styles.inputGroup}>
                        <label style={styles.label}>DIRECCIÓN FÍSICA / LEGAL</label>
                        <input type="text" style={styles.input} placeholder="Av. Principal #123" value={formData.direccion} onChange={(e) => setFormData({...formData, direccion: e.target.value})} required />
                    </div>

                    <hr style={styles.separator} />

                    {/* SECCIÓN 2: PLAN SAAS */}
                    <h3 style={styles.sectionTitle}>2. Suscripción Comercial</h3>
                    <div style={styles.inputGroup}>
                        <label style={styles.label}>PLAN DE FACTURACIÓN (T025)</label>
                        <select style={styles.input} required value={formData.plan_id} onChange={(e) => setFormData({...formData, plan_id: e.target.value})}>
                            <option value="">-- Selecciona un Plan --</option>
                            {planes.map(p => (
                                <option key={p.id} value={p.id}>
                                    {p.nombre}
                                </option>
                            ))}
                        </select>
                    </div>

                    <hr style={styles.separator} />

                    {/* SECCIÓN 3: CUENTA ADMINISTRATIVA */}
                    <h3 style={styles.sectionTitle}>3. Cuenta de Administrador</h3>
                    <div style={styles.grid}>
                        <div style={styles.inputGroup}>
                            <label style={styles.label}>NOMBRE DE USUARIO</label>
                            <input type="text" style={styles.input} placeholder="admin.clinica" value={formData.username} onChange={(e) => setFormData({...formData, username: e.target.value})} required />
                        </div>
                        <div style={styles.inputGroup}>
                            <label style={styles.label}>CONTRASEÑA SEGURA</label>
                            <input type="password" style={styles.input} placeholder="******" value={formData.password} onChange={(e) => setFormData({...formData, password: e.target.value})} required />
                        </div>
                    </div>

                    <div style={styles.inputGroup}>
                        <label style={styles.label}>EMAIL DEL ADMINISTRADOR</label>
                        <input type="email" style={styles.input} placeholder="gerencia@clinica.com" value={formData.email_admin} onChange={(e) => setFormData({...formData, email_admin: e.target.value})} required />
                    </div>

                    <div style={styles.actions}>
                        <button type="button" onClick={() => navigate('/')} style={styles.btnSecondary} disabled={loading}>
                            CANCELAR
                        </button>
                        <button type="submit" style={styles.btnPrimary} disabled={loading}>
                            {loading ? 'CREANDO ENTORNO...' : 'ABRIR CUENTA SAAS'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

const styles = {
    layout: { padding: '40px 0', display: 'flex', justifyContent: 'center', alignItems: 'center', backgroundColor: '#f1f5f9', minHeight: '100vh' },
    card: { width: '600px', backgroundColor: 'white', borderRadius: '12px', boxShadow: '0 10px 25px rgba(0,0,0,0.05)', border: '1px solid #e2e8f0', overflow: 'hidden' },
    cardHeader: { padding: '25px', borderBottom: '1px solid #f1f5f9', textAlign: 'center', backgroundColor: '#0f172a' },
    title: { margin: 0, color: 'white', fontSize: '18px', fontWeight: '800', letterSpacing: '0.5px' },
    subtitle: { margin: '5px 0 0 0', color: '#94a3b8', fontSize: '11px', fontWeight: '600' },
    form: { padding: '30px' },
    sectionTitle: { fontSize: '14px', color: '#1e293b', marginBottom: '15px', marginTop: '0', fontWeight: 'bold' },
    separator: { border: 'none', borderTop: '1px solid #e2e8f0', margin: '20px 0' },
    inputGroup: { marginBottom: '15px' },
    grid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' },
    label: { display: 'block', fontSize: '10px', fontWeight: 'bold', color: '#64748b', marginBottom: '6px', textTransform: 'uppercase' },
    input: { width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '13px', boxSizing: 'border-box', outline: 'none' },
    errorBox: { padding: '12px', backgroundColor: '#fef2f2', color: '#b91c1c', border: '1px solid #fecaca', borderRadius: '6px', marginBottom: '20px', fontSize: '13px' },
    actions: { display: 'flex', gap: '15px', marginTop: '30px' },
    btnPrimary: { flex: 2, padding: '14px', backgroundColor: '#16a34a', color: 'white', border: 'none', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', fontSize: '13px' },
    btnSecondary: { flex: 1, padding: '14px', backgroundColor: 'white', color: '#64748b', border: '1px solid #cbd5e1', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', fontSize: '13px' }
};

export default RegistroClinica;