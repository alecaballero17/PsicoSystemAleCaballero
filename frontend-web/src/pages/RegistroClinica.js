// [CIERRE SPRINT 1] Flujo SaaS integrado según Requerimientos 3.2 y RF-29.
// Con simulación de pasarela de pago Stripe (T025) al seleccionar planes de pago.
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/axiosConfig'; 
import { useAuth } from '../context/AuthContext';

const RealisticQRCode = ({ size = 140 }) => {
    // Generate a 25x25 grid
    const grid = [];
    const N = 25;
    for (let r = 0; r < N; r++) {
        grid[r] = new Array(N).fill(0);
    }

    // Helper to draw a square
    const drawSquare = (row, col, size, value) => {
        for (let r = 0; r < size; r++) {
            for (let c = 0; c < size; c++) {
                if (row + r < N && col + c < N) {
                    grid[row + r][col + c] = value;
                }
            }
        }
    };

    // Draw position detection patterns (7x7)
    const drawFinderPattern = (row, col) => {
        // Outer 7x7 black
        drawSquare(row, col, 7, 1);
        // Inner 5x5 white
        drawSquare(row + 1, col + 1, 5, 0);
        // Center 3x3 black
        drawSquare(row + 2, col + 2, 3, 1);
    };

    drawFinderPattern(0, 0);
    drawFinderPattern(0, N - 7);
    drawFinderPattern(N - 7, 0);

    // Draw timing patterns (dots between finders)
    for (let i = 8; i < N - 8; i++) {
        grid[6][i] = i % 2 === 0 ? 1 : 0;
        grid[i][6] = i % 2 === 0 ? 1 : 0;
    }

    // Alignment pattern (5x5) at (N-9, N-9)
    const alRow = N - 9, alCol = N - 9;
    drawSquare(alRow, alCol, 5, 1);
    drawSquare(alRow + 1, alCol + 1, 3, 0);
    grid[alRow + 2][alCol + 2] = 1;

    // Fill the rest with pseudo-random modules
    let seed = 42;
    const rand = () => {
        seed = (seed * 9301 + 49297) % 233280;
        return seed / 233280.0;
    };

    for (let r = 0; r < N; r++) {
        for (let c = 0; c < N; c++) {
            if (r < 8 && c < 8) continue;
            if (r < 8 && c >= N - 8) continue;
            if (r >= N - 8 && c < 8) continue;
            if (r >= alRow && r < alRow + 5 && c >= alCol && c < alCol + 5) continue;
            if (r === 6 || c === 6) continue;
            
            grid[r][c] = rand() > 0.48 ? 1 : 0; // slightly denser
        }
    }

    // Clear a 5x5 center area for the badge/logo
    const centerStart = Math.floor(N / 2) - 2;
    for (let r = centerStart; r < centerStart + 5; r++) {
        for (let c = centerStart; c < centerStart + 5; c++) {
            grid[r][c] = 0;
        }
    }

    // Render the SVG
    const cellSize = size / N;
    const rects = [];
    for (let r = 0; r < N; r++) {
        for (let c = 0; c < N; c++) {
            if (grid[r][c] === 1) {
                rects.push(
                    <rect
                        key={`${r}-${c}`}
                        x={c * cellSize}
                        y={r * cellSize}
                        width={cellSize}
                        height={cellSize}
                        fill="#0f172a"
                    />
                );
            }
        }
    }

    return (
        <div style={{ position: 'relative', width: size, height: size }}>
            <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
                <rect width={size} height={size} fill="white" />
                {rects}
            </svg>
            <div style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                width: `${size * 0.22}px`,
                height: `${size * 0.22}px`,
                backgroundColor: '#ffffff',
                border: '2px solid #635bff',
                borderRadius: '4px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
                <span style={{ fontSize: `${size * 0.12}px` }}>🔒</span>
            </div>
        </div>
    );
};

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

    // Estados para la pasarela de Stripe Checkout simulada
    const [showPaymentModal, setShowPaymentModal] = useState(false);
    const [paymentMethod, setPaymentMethod] = useState('card'); // 'card' | 'qr'
    const [paymentStep, setPaymentStep] = useState(0); // 0: input, 1: connecting, 2: verifying, 3: approved
    const [cardData, setCardData] = useState({ number: '', expiry: '', cvc: '', name: '' });

    const navigate = useNavigate();

    // Consultamos los planes disponibles públicos e inyectamos estilos spin
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

        // Inyectar animación spin si no existe
        if (!document.getElementById('stripe-spin-style')) {
            const styleSheet = document.createElement("style");
            styleSheet.id = 'stripe-spin-style';
            styleSheet.innerText = `
              @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
              }
            `;
            document.head.appendChild(styleSheet);
        }
    }, [user, navigate]);

    const getPlanPrice = (planId) => {
        if (planId === 'Profesional') return '199 Bs/mes';
        if (planId === 'Premium') return '549 Bs/mes';
        return '0 Bs/mes';
    };

    const handleProcessPayment = (e) => {
        e.preventDefault();
        setPaymentStep(1); // Conectando con Stripe
        
        setTimeout(() => {
            setPaymentStep(2); // Verificando fondos y 3D Secure
            
            setTimeout(() => {
                setPaymentStep(3); // Pago aprobado
                
                setTimeout(() => {
                    setShowPaymentModal(false);
                    // Disparar el flujo real de onboarding
                    handleSubmit();
                }, 1000);
            }, 1200);
        }, 1200);
    };

    const handleSubmit = async (e) => {
        if (e) e.preventDefault();

        // Si el plan es Profesional o Premium y no se ha pagado, abrimos el modal de Stripe
        if ((formData.plan_id === 'Profesional' || formData.plan_id === 'Premium') && !showPaymentModal && paymentStep !== 3) {
            setPaymentStep(0);
            setCardData({ number: '', expiry: '', cvc: '', name: '' });
            setShowPaymentModal(true);
            return;
        }

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
        try {
            // Envío público hacia el onboarding SaaS (Alineado con backend P1)
            await apiClient.post('onboarding/', atomicPayload);
            alert("ALTA EXITOSA: La clínica, la suscripción y tu usuario administrador se crearon correctamente.");
            navigate('/login');
        } catch (err) {
            console.error("Error en alta atómica", err.response?.data || err);
            
            // Mejora: Extraer mensaje de error detallado del backend
            let errorMessage = "No se pudo realizar el alta de la Clínica. Verifica los datos.";
            const serverData = err.response?.data;
            
            if (serverData) {
                if (serverData.detail) errorMessage = serverData.detail;
                else if (serverData.clinica) {
                    const clinicaErrors = serverData.clinica;
                    errorMessage = typeof clinicaErrors === 'string' ? clinicaErrors : Object.values(clinicaErrors).flat().join(" ");
                }
                else if (serverData.admin) {
                    const adminErrors = serverData.admin;
                    errorMessage = typeof adminErrors === 'string' ? adminErrors : Object.values(adminErrors).flat().join(" ");
                }
                else if (typeof serverData === 'object') {
                    errorMessage = Object.values(serverData).flat().join(" ");
                }
            }
            
            setError(errorMessage);
            setPaymentStep(0); // Resetear estado de pago
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

            {/* MODAL STRIPE CHECKOUT SIMULATOR */}
            {showPaymentModal && (
                <div style={styles.modalOverlay}>
                    <div style={styles.modalContent}>
                        <div style={styles.stripeHeader}>
                            <span style={{ fontSize: '16px', fontWeight: 'bold', color: '#0f172a' }}>💳 Stripe Checkout</span>
                            <span style={styles.stripeBadge}>Test Mode</span>
                        </div>
                        
                        {paymentStep === 0 && (
                            <form onSubmit={handleProcessPayment} style={{ marginTop: '20px' }}>
                                <p style={{ margin: '0 0 15px 0', fontSize: '13px', color: '#475569', textAlign: 'left' }}>
                                    Pagar suscripción para el plan <strong>{formData.plan_id}</strong>. 
                                    Monto: <strong style={{ color: '#0f172a' }}>{getPlanPrice(formData.plan_id)}</strong>.
                                </p>

                                {/* Pestañas de Métodos de Pago */}
                                <div style={{ display: 'flex', borderBottom: '2px solid #e2e8f0', marginBottom: '20px' }}>
                                    <button 
                                        type="button" 
                                        style={{
                                            flex: 1, 
                                            padding: '10px', 
                                            border: 'none', 
                                            background: paymentMethod === 'card' ? '#f1f5f9' : 'none',
                                            fontWeight: 'bold',
                                            borderBottom: paymentMethod === 'card' ? '2px solid #635bff' : 'none',
                                            color: paymentMethod === 'card' ? '#635bff' : '#64748b',
                                            cursor: 'pointer'
                                        }}
                                        onClick={() => setPaymentMethod('card')}
                                    >
                                        💳 Tarjeta
                                    </button>
                                    <button 
                                        type="button" 
                                        style={{
                                            flex: 1, 
                                            padding: '10px', 
                                            border: 'none', 
                                            background: paymentMethod === 'qr' ? '#f1f5f9' : 'none',
                                            fontWeight: 'bold',
                                            borderBottom: paymentMethod === 'qr' ? '2px solid #635bff' : 'none',
                                            color: paymentMethod === 'qr' ? '#635bff' : '#64748b',
                                            cursor: 'pointer'
                                        }}
                                        onClick={() => setPaymentMethod('qr')}
                                    >
                                        📱 Código QR
                                    </button>
                                </div>

                                {paymentMethod === 'card' ? (
                                    <>
                                        <div style={styles.modalInputGroup}>
                                            <label style={styles.modalLabel}>Número de Tarjeta</label>
                                            <input 
                                                required 
                                                type="text" 
                                                placeholder="4242 4242 4242 4242" 
                                                value={cardData.number} 
                                                onChange={e => setCardData({...cardData, number: e.target.value})} 
                                                style={styles.modalInput} 
                                            />
                                        </div>
                                        <div style={{ display: 'flex', gap: '10px' }}>
                                            <div style={{ ...styles.modalInputGroup, flex: 1 }}>
                                                <label style={styles.modalLabel}>Expiración</label>
                                                <input 
                                                    required 
                                                    type="text" 
                                                    placeholder="MM / YY" 
                                                    value={cardData.expiry} 
                                                    onChange={e => setCardData({...cardData, expiry: e.target.value})} 
                                                    style={styles.modalInput} 
                                                />
                                            </div>
                                            <div style={{ ...styles.modalInputGroup, flex: 1 }}>
                                                <label style={styles.modalLabel}>CVC</label>
                                                <input 
                                                    required 
                                                    type="password" 
                                                    maxLength="4" 
                                                    placeholder="123" 
                                                    value={cardData.cvc} 
                                                    onChange={e => setCardData({...cardData, cvc: e.target.value})} 
                                                    style={styles.modalInput} 
                                                />
                                            </div>
                                        </div>
                                        <div style={styles.modalInputGroup}>
                                            <label style={styles.modalLabel}>Titular de la Tarjeta</label>
                                            <input 
                                                required 
                                                type="text" 
                                                placeholder="Nombre completo" 
                                                value={cardData.name} 
                                                onChange={e => setCardData({...cardData, name: e.target.value})} 
                                                style={styles.modalInput} 
                                            />
                                        </div>
                                    </>
                                ) : (
                                    <div style={{ textAlign: 'center', padding: '10px 0' }}>
                                        <p style={{ fontSize: '13px', color: '#64748b', marginBottom: '15px' }}>
                                            Escanea el código QR desde tu app bancaria móvil para efectuar el pago seguro.
                                        </p>
                                        <div style={{
                                            margin: '0 auto 15px auto',
                                            width: '200px',
                                            backgroundColor: '#f8fafc',
                                            border: '1px solid #e2e8f0',
                                            borderRadius: '12px',
                                            padding: '15px',
                                            boxSizing: 'border-box',
                                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                                            display: 'flex',
                                            flexDirection: 'column',
                                            alignItems: 'center'
                                        }}>
                                            <div style={{
                                                backgroundColor: 'white',
                                                padding: '10px',
                                                borderRadius: '8px',
                                                boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
                                            }}>
                                                <RealisticQRCode size={140} />
                                            </div>
                                            <div style={{ marginTop: '10px', textAlign: 'center' }}>
                                                <span style={{ fontSize: '10px', fontWeight: 'bold', color: '#0f172a', letterSpacing: '1px' }}>SIMPLE-STRIPE-PAY</span>
                                                <div style={{ fontSize: '12px', fontWeight: 'bold', color: '#635bff', marginTop: '2px' }}>
                                                    {formData.plan_id === 'Profesional' ? '199.00' : '549.00'} BS
                                                </div>
                                            </div>
                                        </div>
                                        <span style={{ fontSize: '11px', color: '#16a34a', fontWeight: 'bold' }}>✓ Código generado exitosamente</span>
                                    </div>
                                )}

                                <div style={{ display: 'flex', gap: '10px', marginTop: '25px' }}>
                                    <button type="button" style={{ ...styles.btnSecondary, flex: 1, padding: '12px' }} onClick={() => setShowPaymentModal(false)}>
                                        Cancelar
                                    </button>
                                    <button type="submit" style={{ ...styles.btnPrimary, flex: 2, padding: '12px', backgroundColor: '#635bff' }}>
                                        {paymentMethod === 'card' ? 'Pagar con Tarjeta' : 'Confirmar Pago QR'}
                                    </button>
                                </div>
                            </form>
                        )}

                        {paymentStep > 0 && (
                            <div style={{ textAlign: 'center', padding: '40px 0' }}>
                                {paymentStep === 1 && (
                                    <>
                                        <div style={styles.spinner}></div>
                                        <h3 style={{ color: '#0f172a', marginTop: '20px' }}>Conectando con Stripe...</h3>
                                        <p style={{ color: '#64748b', fontSize: '13px' }}>Abriendo canal seguro y tokenizando datos.</p>
                                    </>
                                )}
                                {paymentStep === 2 && (
                                    <>
                                        <div style={styles.spinner}></div>
                                        <h3 style={{ color: '#0f172a', marginTop: '20px' }}>Verificando pago y 3D Secure...</h3>
                                        <p style={{ color: '#64748b', fontSize: '13px' }}>Autorizando transacción con el banco emisor.</p>
                                    </>
                                )}
                                {paymentStep === 3 && (
                                    <>
                                        <div style={{ fontSize: '50px', color: '#16a34a' }}>✓</div>
                                        <h3 style={{ color: '#166534', marginTop: '20px' }}>¡Pago Aprobado con Éxito!</h3>
                                        <p style={{ color: '#64748b', fontSize: '13px' }}>Registrando clínica en el sistema SaaS...</p>
                                    </>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            )}
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
    btnSecondary: { flex: 1, padding: '14px', backgroundColor: 'white', color: '#64748b', border: '1px solid #cbd5e1', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', fontSize: '13px' },
    
    // Modal Stripe
    modalOverlay: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(15, 23, 42, 0.6)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 },
    modalContent: { backgroundColor: 'white', padding: '30px', borderRadius: '16px', width: '100%', maxWidth: '440px', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.2)' },
    stripeHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #cbd5e1', paddingBottom: '15px' },
    stripeBadge: { backgroundColor: '#635bff', color: 'white', fontSize: '10px', fontWeight: 'bold', padding: '4px 8px', borderRadius: '4px' },
    modalInputGroup: { marginBottom: '15px', textAlign: 'left' },
    modalLabel: { display: 'block', marginBottom: '5px', fontSize: '12px', fontWeight: 'bold', color: '#475569', textTransform: 'uppercase' },
    modalInput: { width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1', boxSizing: 'border-box', fontSize: '14px' },
    spinner: {
        width: '40px',
        height: '40px',
        border: '4px solid #e2e8f0',
        borderTop: '4px solid #635bff',
        borderRadius: '50%',
        margin: '0 auto',
        animation: 'spin 1s linear infinite'
    }
};

export default RegistroClinica;