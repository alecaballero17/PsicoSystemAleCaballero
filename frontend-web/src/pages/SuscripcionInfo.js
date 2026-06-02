// [SPRINT 1 - T025] Interfaz de monitoreo de límites SaaS.
// Componente de visualización de Suscripción para el Administrador de la Clínica con Simulación Stripe Checkout integrada.

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/axiosConfig';
import authService from '../services/authService';

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

export const SuscripcionInfo = () => {
    const navigate = useNavigate();
    const [info, setInfo] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [showModal, setShowModal] = useState(false);
    const [targetPlan, setTargetPlan] = useState(null);
    const [paymentMethod, setPaymentMethod] = useState('card'); // 'card' | 'qr'
    const [step, setStep] = useState(0); // 0: input, 1: connecting, 2: verifying, 3: approved
    const [cardData, setCardData] = useState({ number: '', expiry: '', cvc: '', name: '' });
    const [clinicaId, setClinicaId] = useState(null);

    const fetchSuscripcionData = async () => {
        try {
            setLoading(true);
            const user = await authService.getCurrentUser();
            if (!user || !user.clinica_id) {
                setError('No tienes una clínica asignada o eres SuperAdmin.');
                setLoading(false);
                return;
            }
            setClinicaId(user.clinica_id);

            const response = await apiClient.get(`suscripciones/${user.clinica_id}/`);
            setInfo(response.data);
            setError('');
        } catch (err) {
            console.error(err);
            setError('Error al obtener la información de la suscripción.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSuscripcionData();
    }, []);

    const handleUpgradeClick = (planCode) => {
        setTargetPlan(planCode);
        setStep(0);
        setCardData({ number: '', expiry: '', cvc: '', name: '' });
        setShowModal(true);
    };

    const handleProcessPayment = (e) => {
        e.preventDefault();
        
        // Simular flujo de Stripe Checkout
        setStep(1); // Conectando con Stripe
        
        setTimeout(() => {
            setStep(2); // Verificando fondos y 3D Secure
            
            setTimeout(() => {
                setStep(3); // Pago aprobado
                
                setTimeout(async () => {
                    try {
                        // Guardar en backend
                        await apiClient.put(`suscripciones/${clinicaId}/`, {
                            plan_suscripcion: targetPlan
                        });
                        alert(`¡Pago completado con éxito mediante Stripe! Tu clínica ha sido actualizada al ${targetPlan === 'Profesional' ? 'Plan Profesional' : 'Plan Premium'}.`);
                        setShowModal(false);
                        fetchSuscripcionData(); // Refrescar límites
                    } catch (err) {
                        alert("Error al actualizar la suscripción en el servidor.");
                        setStep(0);
                    }
                }, 1000);
            }, 1200);
        }, 1200);
    };

    const getPlanDetails = (planCode) => {
        if (planCode === 'Basico') {
            return { price: '0 Bs/mes', pacientes: '5', psicologos: '2', desc: 'Ideal para consultorios pequeños de inicio rápido.' };
        } else if (planCode === 'Profesional') {
            return { price: '199 Bs/mes', pacientes: '20', psicologos: '10', desc: 'Para clínicas en crecimiento que requieren mayor volumen de pacientes.' };
        } else {
            return { price: '549 Bs/mes', pacientes: 'Ilimitados', psicologos: 'Ilimitados', desc: 'Acceso corporativo full sin límites operacionales ni cuotas.' };
        }
    };

    const getBadgeStyle = (estado) => {
        return { backgroundColor: '#dcfce7', color: '#166534', padding: '5px 10px', borderRadius: '12px', fontWeight: 'bold' };
    };

    return (
        <div style={styles.container}>
            <header style={styles.header}>
                <div>
                    <h1 style={styles.headerTitle}>Suscripción SaaS (CU-24)</h1>
                    <p style={styles.headerSubtitle}>Monitoreo de Límites y Control de Licencia</p>
                </div>
                <button style={styles.btnSecondary} onClick={() => navigate('/dashboard')}>
                    Volver al Dashboard
                </button>
            </header>

            {loading ? (
                <div style={{ textAlign: 'center', marginTop: '50px' }}>
                    <p style={{ color: '#64748b' }}>Consultando estado de suscripción y cuotas...</p>
                </div>
            ) : error ? (
                <div style={styles.errorBox}>{error}</div>
            ) : (
                <>
                    {/* Tarjeta de Límites Actuales */}
                    <div style={styles.card}>
                        <h2 style={{ margin: '0 0 20px 0', color: '#0f172a', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span>Clínica: {info.clinica_nombre}</span>
                            <span style={getBadgeStyle(info.estado)}>
                                {info.plan_nombre} ({info.estado} ✅)
                            </span>
                        </h2>
                        
                        <h3 style={{ margin: '0 0 20px 0', color: '#475569', fontSize: '15px' }}>📈 Cupos y Límites de Uso Actual</h3>
                        
                        <div style={styles.limitsGrid}>
                            {/* Cupo Pacientes */}
                            <div style={styles.limitBox}>
                                <div style={{ fontSize: '32px', marginBottom: '10px' }}>🏃</div>
                                <p style={styles.limitTitle}>Pacientes Registrados</p>
                                <p style={styles.limitRatio}>
                                    <span style={styles.actual}>{info.uso.pacientes_actuales}</span>
                                    <span style={styles.divider}>/</span>
                                    <span style={styles.maximo}>{info.uso.pacientes_limite === 9999 ? '∞' : info.uso.pacientes_limite}</span>
                                </p>
                                <div style={styles.progressBarBg}>
                                    <div style={{
                                        ...styles.progressBarFill,
                                        width: `${Math.min(100, (info.uso.pacientes_actuales / info.uso.pacientes_limite) * 100)}%`,
                                        backgroundColor: (info.uso.pacientes_actuales >= info.uso.pacientes_limite) ? '#ef4444' : '#2563eb'
                                    }} />
                                </div>
                                <p style={{ fontSize: '11px', color: '#64748b', marginTop: '10px' }}>
                                    Límite establecido por plan.
                                </p>
                            </div>

                            {/* Cupo Psicólogos */}
                            <div style={styles.limitBox}>
                                <div style={{ fontSize: '32px', marginBottom: '10px' }}>⚕️</div>
                                <p style={styles.limitTitle}>Psicólogos Habilitados</p>
                                <p style={styles.limitRatio}>
                                    <span style={styles.actual}>{info.uso.psicologos_actuales}</span>
                                    <span style={styles.divider}>/</span>
                                    <span style={styles.maximo}>{info.uso.psicologos_limite === 9999 ? '∞' : info.uso.psicologos_limite}</span>
                                </p>
                                <div style={styles.progressBarBg}>
                                    <div style={{
                                        ...styles.progressBarFill,
                                        width: `${Math.min(100, (info.uso.psicologos_actuales / info.uso.psicologos_limite) * 100)}%`,
                                        backgroundColor: (info.uso.psicologos_actuales >= info.uso.psicologos_limite) ? '#ef4444' : '#16a34a'
                                    }} />
                                </div>
                                <p style={{ fontSize: '11px', color: '#64748b', marginTop: '10px' }}>
                                    Límite establecido por plan.
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Planes Disponibles (Incentivos de Upgrade) */}
                    <div style={{ marginTop: '40px' }}>
                        <h2 style={{ textAlign: 'center', color: '#0f172a', marginBottom: '10px' }}>Selecciona el Plan Ideal para tu Clínica</h2>
                        <p style={{ textAlign: 'center', color: '#64748b', marginBottom: '30px' }}>Aumenta tus cuotas operativas y desbloquea el máximo potencial con cobros seguros.</p>
                        
                        <div style={styles.pricingGrid}>
                            {/* PLAN BASICO */}
                            <div style={{
                                ...styles.pricingCard,
                                ...(info.plan_nombre.includes('Básico') ? styles.pricingCardActive : {})
                            }}>
                                {info.plan_nombre.includes('Básico') && <span style={styles.activePlanLabel}>PLAN ACTIVO</span>}
                                <h3 style={styles.planName}>Básico (Gratuito)</h3>
                                <p style={styles.planDesc}>{getPlanDetails('Basico').desc}</p>
                                <div style={styles.planPrice}>{getPlanDetails('Basico').price}</div>
                                <ul style={styles.planFeatures}>
                                    <li>✔ Hasta <strong>5 Pacientes</strong> registrados</li>
                                    <li>✔ Hasta <strong>2 Psicólogos</strong> colaboradores</li>
                                    <li>✔ Bitácora de Sucesos y Auditoría</li>
                                    <li>✔ Diagnósticos Clínicos IA</li>
                                </ul>
                                <button disabled style={styles.btnPlanDisabled}>
                                    Gratuito por defecto
                                </button>
                            </div>

                            {/* PLAN PROFESIONAL */}
                            <div style={{
                                ...styles.pricingCard,
                                ...(info.plan_nombre.includes('Profesional') ? styles.pricingCardActive : {})
                            }}>
                                {info.plan_nombre.includes('Profesional') && <span style={styles.activePlanLabel}>PLAN ACTIVO</span>}
                                <h3 style={styles.planName}>Profesional</h3>
                                <p style={styles.planDesc}>{getPlanDetails('Profesional').desc}</p>
                                <div style={styles.planPrice}>{getPlanDetails('Profesional').price}</div>
                                <ul style={styles.planFeatures}>
                                    <li>✔ Hasta <strong>20 Pacientes</strong> registrados</li>
                                    <li>✔ Hasta <strong>10 Psicólogos</strong> colaboradores</li>
                                    <li>✔ Bitácora de Sucesos y Auditoría</li>
                                    <li>✔ Diagnósticos Clínicos IA</li>
                                    <li>✔ Soporte Estándar por Correo</li>
                                </ul>
                                {info.plan_nombre.includes('Profesional') ? (
                                    <button disabled style={styles.btnPlanDisabled}>Plan Actual</button>
                                ) : info.plan_nombre.includes('Premium') ? (
                                    <button disabled style={styles.btnPlanDisabled}>Downgrade no disponible</button>
                                ) : (
                                    <button style={styles.btnPlanUpgrade} onClick={() => handleUpgradeClick('Profesional')}>
                                        Elegir Plan Profesional
                                    </button>
                                )}
                            </div>

                            {/* PLAN PREMIUM */}
                            <div style={{
                                ...styles.pricingCard,
                                ...(info.plan_nombre.includes('Premium') ? styles.pricingCardActive : {})
                            }}>
                                {info.plan_nombre.includes('Premium') && <span style={styles.activePlanLabel}>PLAN ACTIVO</span>}
                                <h3 style={styles.planName}>Premium</h3>
                                <p style={styles.planDesc}>{getPlanDetails('Premium').desc}</p>
                                <div style={styles.planPrice}>{getPlanDetails('Premium').price}</div>
                                <ul style={styles.planFeatures}>
                                    <li>✔ <strong>Pacientes Ilimitados</strong></li>
                                    <li>✔ <strong>Psicólogos Ilimitados</strong></li>
                                    <li>✔ Bitácora de Sucesos y Auditoría</li>
                                    <li>✔ Diagnósticos Clínicos IA</li>
                                    <li>✔ Soporte Prioritario 24/7</li>
                                    <li>✔ Backups Automáticos en la Nube</li>
                                </ul>
                                {info.plan_nombre.includes('Premium') ? (
                                    <button disabled style={styles.btnPlanDisabled}>Plan Actual</button>
                                ) : (
                                    <button style={styles.btnPlanUpgradePremium} onClick={() => handleUpgradeClick('Premium')}>
                                        Elegir Plan Premium
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* MODAL STRIPE CHECKOUT SIMULATOR */}
                    {showModal && (
                        <div style={styles.modalOverlay}>
                            <div style={styles.modalContent}>
                                <div style={styles.stripeHeader}>
                                    <span style={{ fontSize: '18px', fontWeight: 'bold' }}>💳 Stripe Checkout</span>
                                    <span style={styles.stripeBadge}>Test Mode</span>
                                </div>
                                
                                {step === 0 && (
                                    <form onSubmit={handleProcessPayment} style={{ marginTop: '20px' }}>
                                        <p style={{ margin: '0 0 15px 0', fontSize: '14px', color: '#475569' }}>
                                            Actualizar al <strong>{targetPlan === 'Profesional' ? 'Plan Profesional' : 'Plan Premium'}</strong>. 
                                            Monto a pagar: <strong style={{ color: '#0f172a' }}>{getPlanDetails(targetPlan).price}</strong>.
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
                                                💳 Tarjeta de Crédito
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
                                                📱 Pago por QR
                                            </button>
                                        </div>

                                        {paymentMethod === 'card' ? (
                                            <>
                                                <div style={styles.inputGroup}>
                                                    <label style={styles.label}>Número de Tarjeta</label>
                                                    <input 
                                                        required 
                                                        type="text" 
                                                        placeholder="4242 4242 4242 4242" 
                                                        value={cardData.number} 
                                                        onChange={e => setCardData({...cardData, number: e.target.value})} 
                                                        style={styles.input} 
                                                    />
                                                </div>
                                                <div style={{ display: 'flex', gap: '10px' }}>
                                                    <div style={{ ...styles.inputGroup, flex: 1 }}>
                                                        <label style={styles.label}>Expiración</label>
                                                        <input 
                                                            required 
                                                            type="text" 
                                                            placeholder="MM / YY" 
                                                            value={cardData.expiry} 
                                                            onChange={e => setCardData({...cardData, expiry: e.target.value})} 
                                                            style={styles.input} 
                                                        />
                                                    </div>
                                                    <div style={{ ...styles.inputGroup, flex: 1 }}>
                                                        <label style={styles.label}>CVC</label>
                                                        <input 
                                                            required 
                                                            type="password" 
                                                            maxLength="4" 
                                                            placeholder="123" 
                                                            value={cardData.cvc} 
                                                            onChange={e => setCardData({...cardData, cvc: e.target.value})} 
                                                            style={styles.input} 
                                                        />
                                                    </div>
                                                </div>
                                                <div style={styles.inputGroup}>
                                                    <label style={styles.label}>Titular de la Tarjeta</label>
                                                    <input 
                                                        required 
                                                        type="text" 
                                                        placeholder="Nombre completo" 
                                                        value={cardData.name} 
                                                        onChange={e => setCardData({...cardData, name: e.target.value})} 
                                                        style={styles.input} 
                                                    />
                                                </div>
                                            </>
                                        ) : (
                                            <div style={{ textAlign: 'center', padding: '10px 0' }}>
                                                <p style={{ fontSize: '13px', color: '#64748b', marginBottom: '15px' }}>
                                                    Escanea el código QR desde tu app bancaria móvil para efectuar el pago de forma segura a través de Stripe/Simple.
                                                </p>
                                                {/* Código QR Realista */}
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
                                                            {targetPlan === 'Profesional' ? '199.00' : '549.00'} BS
                                                        </div>
                                                    </div>
                                                </div>
                                                <span style={{ fontSize: '11px', color: '#16a34a', fontWeight: 'bold' }}>✓ Código generado exitosamente</span>
                                            </div>
                                        )}

                                        <div style={{ display: 'flex', gap: '10px', marginTop: '25px' }}>
                                            <button type="button" style={{ ...styles.btnSecondary, flex: 1, padding: '12px', border: '1px solid #cbd5e1', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }} onClick={() => setShowModal(false)}>
                                                Cancelar
                                            </button>
                                            <button type="submit" style={{ ...styles.btnPrimary, flex: 2, padding: '12px', backgroundColor: '#635bff', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
                                                {paymentMethod === 'card' ? 'Pagar con Tarjeta (Stripe)' : 'Confirmar Pago QR'}
                                            </button>
                                        </div>
                                    </form>
                                )}

                                {step > 0 && (
                                    <div style={{ textAlign: 'center', padding: '40px 0' }}>
                                        {step === 1 && (
                                            <>
                                                <div style={styles.spinner}></div>
                                                <h3 style={{ color: '#0f172a', marginTop: '20px' }}>Conectando con Stripe...</h3>
                                                <p style={{ color: '#64748b', fontSize: '13px' }}>Abriendo canal seguro y tokenizando datos.</p>
                                            </>
                                        )}
                                        {step === 2 && (
                                            <>
                                                <div style={styles.spinner}></div>
                                                <h3 style={{ color: '#0f172a', marginTop: '20px' }}>Verificando pago y 3D Secure...</h3>
                                                <p style={{ color: '#64748b', fontSize: '13px' }}>Autorizando transacción con el banco emisor.</p>
                                            </>
                                        )}
                                        {step === 3 && (
                                            <>
                                                <div style={{ fontSize: '50px', color: '#16a34a' }}>✓</div>
                                                <h3 style={{ color: '#166534', marginTop: '20px' }}>¡Pago Aprobado con Éxito!</h3>
                                                <p style={{ color: '#64748b', fontSize: '13px' }}>Suscripción autorizada. Actualizando base de datos...</p>
                                            </>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

// ===============================================
// ESTILOS PREMIUM
// ===============================================
const styles = {
    container: { padding: '30px', maxWidth: '1000px', margin: '0 auto', backgroundColor: '#f8fafc', minHeight: '100vh' },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' },
    headerTitle: { margin: 0, fontSize: '24px', color: '#0f172a' },
    headerSubtitle: { margin: 0, fontSize: '14px', color: '#64748b' },
    btnSecondary: { backgroundColor: '#fff', color: '#475569', padding: '10px 16px', border: '1px solid #cbd5e1', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' },
    errorBox: { padding: '15px', backgroundColor: '#fef2f2', color: '#b91c1c', border: '1px solid #fecaca', borderRadius: '8px' },
    card: { backgroundColor: 'white', borderRadius: '16px', padding: '35px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)', marginBottom: '30px' },
    limitsGrid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px', marginTop: '20px' },
    limitBox: { border: '1px solid #e2e8f0', borderRadius: '16px', padding: '25px', textAlign: 'center', backgroundColor: '#fafaf9' },
    limitTitle: { margin: '0 0 15px 0', fontSize: '15px', fontWeight: 'bold', color: '#475569' },
    limitRatio: { margin: '0 0 15px 0', display: 'flex', justifyContent: 'center', alignItems: 'baseline', gap: '8px' },
    actual: { fontSize: '36px', fontWeight: '900', color: '#0f172a' },
    divider: { fontSize: '24px', color: '#cbd5e1', fontWeight: '300' },
    maximo: { fontSize: '20px', color: '#94a3b8', fontWeight: 'bold' },
    progressBarBg: { width: '100%', height: '8px', backgroundColor: '#e2e8f0', borderRadius: '4px', overflow: 'hidden' },
    progressBarFill: { height: '100%', borderRadius: '4px', transition: 'width 0.5s ease-out' },
    
    // Grilla de Precios
    pricingGrid: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginTop: '20px' },
    pricingCard: { 
        backgroundColor: 'white', 
        borderRadius: '16px', 
        padding: '30px', 
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)', 
        position: 'relative', 
        border: '2px solid transparent',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        transition: 'all 0.3s ease'
    },
    pricingCardActive: {
        borderColor: '#2563eb',
        boxShadow: '0 10px 15px -3px rgba(37, 99, 235, 0.2)'
    },
    activePlanLabel: {
        position: 'absolute',
        top: '15px',
        right: '15px',
        backgroundColor: '#2563eb',
        color: 'white',
        fontSize: '10px',
        fontWeight: 'bold',
        padding: '4px 8px',
        borderRadius: '12px'
    },
    planName: { fontSize: '20px', margin: '0 0 10px 0', color: '#0f172a', fontWeight: 'bold' },
    planDesc: { fontSize: '13px', color: '#64748b', margin: '0 0 20px 0', minHeight: '40px' },
    planPrice: { fontSize: '28px', fontWeight: '900', color: '#0f172a', margin: '0 0 20px 0' },
    planFeatures: { listStyle: 'none', padding: 0, margin: '0 0 30px 0', fontSize: '13px', color: '#334155', display: 'flex', flexDirection: 'column', gap: '10px' },
    
    btnPlanDisabled: { width: '100%', padding: '12px', border: 'none', borderRadius: '8px', backgroundColor: '#e2e8f0', color: '#94a3b8', fontWeight: 'bold', cursor: 'not-allowed' },
    btnPlanUpgrade: { width: '100%', padding: '12px', border: '2px solid #2563eb', borderRadius: '8px', backgroundColor: 'transparent', color: '#2563eb', fontWeight: 'bold', cursor: 'pointer', transition: 'all 0.2s' },
    btnPlanUpgradePremium: { width: '100%', padding: '12px', border: 'none', borderRadius: '8px', backgroundColor: '#2563eb', color: 'white', fontWeight: 'bold', cursor: 'pointer', transition: 'all 0.2s' },

    // Modal Stripe
    modalOverlay: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(15, 23, 42, 0.6)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 },
    modalContent: { backgroundColor: 'white', padding: '30px', borderRadius: '16px', width: '100%', maxWidth: '440px', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.2)' },
    stripeHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #cbd5e1', paddingBottom: '15px' },
    stripeBadge: { backgroundColor: '#635bff', color: 'white', fontSize: '10px', fontWeight: 'bold', padding: '4px 8px', borderRadius: '4px' },
    inputGroup: { marginBottom: '15px' },
    label: { display: 'block', marginBottom: '5px', fontSize: '12px', fontWeight: 'bold', color: '#475569', textTransform: 'uppercase' },
    input: { width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1', boxSizing: 'border-box', fontSize: '14px' },
    
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

// Agregar estilos globales necesarios para animar el spinner de Stripe
const styleSheet = document.createElement("style");
styleSheet.innerText = `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;
document.head.appendChild(styleSheet);

export default SuscripcionInfo;
