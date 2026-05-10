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
        first_name: '',
        last_name: '',
        // Selección de Plan
        plan_id: ''
    });
    const [planes, setPlanes] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [showStripeMock, setShowStripeMock] = useState(false);

    const navigate = useNavigate();

    // Consultamos los planes disponibles públicos
    useEffect(() => {
        const fetchPlanes = async () => {
            try {
                // T025: Endpoint de catálogo de planes con precios
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

    const handleInitialSubmit = (e) => {
        e.preventDefault();
        setError(null);

        const planSeleccionado = planes.find(p => p.id === formData.plan_id);
        if (planSeleccionado && planSeleccionado.precio > 0) {
            // Mostrar pasarela de pago simulada
            setShowStripeMock(true);
        } else {
            // Plan gratis, proceder directo
            executeRegistration();
        }
    };

    const executeRegistration = async () => {
        setLoading(true);
        setShowStripeMock(false);
        
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
                password: formData.password,
                first_name: formData.first_name,
                last_name: formData.last_name
            },
            plan_id: formData.plan_id
        };

        try {
            // Envío público hacia el onboarding SaaS
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

    const getSelectedPlanDetails = () => {
        return planes.find(p => p.id === formData.plan_id);
    };

    return (
        <div style={styles.layout}>
            {/* Modal Mock de Stripe */}
            {showStripeMock && (
                <div style={styles.stripeOverlay}>
                    <div style={styles.stripeCard}>
                        <div style={styles.stripeHeader}>
                            <span style={styles.stripeLogo}>stripe</span>
                            <button onClick={() => setShowStripeMock(false)} style={styles.closeBtn}>×</button>
                        </div>
                        <div style={styles.stripeBody}>
                            <h3 style={{ margin: '0 0 10px 0', color: '#1e293b' }}>Pagar Suscripción</h3>
                            <p style={{ margin: '0 0 20px 0', color: '#64748b', fontSize: '14px' }}>
                                Estás a punto de suscribir <strong>{formData.nombre}</strong> al plan <strong>{getSelectedPlanDetails()?.nombre}</strong>.
                            </p>
                            <div style={styles.priceTag}>
                                ${getSelectedPlanDetails()?.precio} <span style={{fontSize:'14px', fontWeight:'normal'}}>/ período</span>
                            </div>
                            
                            <div style={styles.mockCardInput}>
                                <div style={{ color: '#94a3b8', marginBottom: '8px', fontSize: '12px' }}>Tarjeta de Crédito / Débito</div>
                                <div style={{ display: 'flex', gap: '10px' }}>
                                    <input type="text" placeholder="**** **** **** 4242" disabled style={styles.mockInput} />
                                    <input type="text" placeholder="MM/AA" disabled style={{...styles.mockInput, width: '70px'}} />
                                    <input type="text" placeholder="CVC" disabled style={{...styles.mockInput, width: '70px'}} />
                                </div>
                            </div>
                            
                            <button onClick={executeRegistration} style={styles.btnStripePay} disabled={loading}>
                                {loading ? 'PROCESANDO...' : `PAGAR $${getSelectedPlanDetails()?.precio}`}
                            </button>
                            <p style={{textAlign: 'center', fontSize: '11px', color: '#94a3b8', marginTop: '10px'}}>
                                🔒 Pagos seguros protegidos (Simulación)
                            </p>
                        </div>
                    </div>
                </div>
            )}

            <div style={styles.card}>
                <header style={styles.cardHeader}>
                    <h2 style={styles.title}>REGISTRO DE UNIDAD CLÍNICA</h2>
                    <p style={styles.subtitle}>Alta SaaS Corporativa (Multi-tenant) - RF-29</p>
                </header>

                <form onSubmit={handleInitialSubmit} style={styles.form}>
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
                                    {p.nombre} - {p.precio > 0 ? `$${p.precio}` : 'Gratis'}
                                </option>
                            ))}
                        </select>
                        {formData.plan_id && getSelectedPlanDetails() && (
                            <div style={{ marginTop: '10px', padding: '12px', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '13px', color: '#475569' }}>
                                <strong>Beneficios:</strong> {getSelectedPlanDetails().beneficios}
                            </div>
                        )}
                    </div>

                    <hr style={styles.separator} />

                    {/* SECCIÓN 3: CUENTA ADMINISTRATIVA */}
                    <h3 style={styles.sectionTitle}>3. Cuenta de Administrador</h3>
                    <div style={styles.grid}>
                        <div style={styles.inputGroup}>
                            <label style={styles.label}>NOMBRE (EJ. GERENTE)</label>
                            <input type="text" style={styles.input} placeholder="Juan" value={formData.first_name} onChange={(e) => setFormData({...formData, first_name: e.target.value})} required />
                        </div>
                        <div style={styles.inputGroup}>
                            <label style={styles.label}>APELLIDO</label>
                            <input type="text" style={styles.input} placeholder="Pérez" value={formData.last_name} onChange={(e) => setFormData({...formData, last_name: e.target.value})} required />
                        </div>
                    </div>

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
                            {loading ? 'CREANDO ENTORNO...' : 'CONTINUAR'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

const styles = {
    layout: { padding: '40px 0', display: 'flex', justifyContent: 'center', alignItems: 'center', backgroundColor: '#f1f5f9', minHeight: '100vh', position: 'relative' },
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
    btnSecondary: { flex: 1, padding: '14px', backgroundColor: 'white', color: '#64748b', border: '1px solid #cbd5e1', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', fontSize: '13px' },
    // Mock Stripe Styles
    stripeOverlay: { position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', backgroundColor: 'rgba(0,0,0,0.6)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 9999, backdropFilter: 'blur(4px)' },
    stripeCard: { width: '400px', backgroundColor: 'white', borderRadius: '12px', overflow: 'hidden', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04)' },
    stripeHeader: { backgroundColor: '#635BFF', padding: '16px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
    stripeLogo: { color: 'white', fontWeight: '900', fontSize: '24px', letterSpacing: '-1px' },
    closeBtn: { background: 'none', border: 'none', color: 'white', fontSize: '24px', cursor: 'pointer' },
    stripeBody: { padding: '30px' },
    priceTag: { fontSize: '32px', fontWeight: '800', color: '#0f172a', marginBottom: '24px' },
    mockCardInput: { border: '1px solid #e2e8f0', padding: '12px', borderRadius: '8px', marginBottom: '20px', backgroundColor: '#f8fafc' },
    mockInput: { padding: '8px', border: '1px solid #cbd5e1', borderRadius: '4px', backgroundColor: '#e2e8f0', color: '#94a3b8', fontSize: '13px' },
    btnStripePay: { width: '100%', padding: '14px', backgroundColor: '#635BFF', color: 'white', border: 'none', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer', fontSize: '14px', boxShadow: '0 4px 6px -1px rgba(99, 91, 255, 0.4)' }
};

export default RegistroClinica;