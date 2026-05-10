import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/axiosConfig';
import authService from '../services/authService';

export const SuscripcionInfo = () => {
    const navigate = useNavigate();
    const [info, setInfo] = useState(null);
    const [transacciones, setTransacciones] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [montoCarga, setMontoCarga] = useState('');
    const [cargandoSaldo, setCargandoSaldo] = useState(false);

    const fetchData = async () => {
        try {
            setLoading(true);
            const user = await authService.getCurrentUser(localStorage.getItem('token'));
            if (!user.clinica) {
                setError('No tienes una clínica asignada.');
                setLoading(false);
                return;
            }

            const [infoRes, transRes] = await Promise.all([
                apiClient.get(`suscripciones/${user.clinica}/`),
                apiClient.get(`suscripciones/transacciones/`)
            ]);

            setInfo(infoRes.data);
            setTransacciones(transRes.data);
        } catch (err) {
            console.error(err);
            setError('Error al obtener la información de la suscripción.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleCargarSaldo = async (e) => {
        e.preventDefault();
        if (!montoCarga || isNaN(montoCarga) || montoCarga <= 0) {
            alert("Ingrese un monto válido.");
            return;
        }

        try {
            setCargandoSaldo(true);
            await apiClient.post('suscripciones/cargar-saldo/', {
                monto: montoCarga,
                descripcion: "Carga de saldo desde panel administrativo",
                metodo_pago: "TARJETA_WEB"
            });
            alert("Saldo cargado exitosamente.");
            setMontoCarga('');
            fetchData();
        } catch (err) {
            alert("Error al cargar saldo.");
        } finally {
            setCargandoSaldo(false);
        }
    };

    const getBadgeStyle = (estado) => {
        switch (estado) {
            case 'ACTIVA': return { backgroundColor: '#dcfce7', color: '#166534', padding: '5px 12px', borderRadius: '20px', fontWeight: 'bold', fontSize: '11px' };
            case 'SUSPENDIDA': return { backgroundColor: '#fee2e2', color: '#991b1b', padding: '5px 12px', borderRadius: '20px', fontWeight: 'bold', fontSize: '11px' };
            default: return { backgroundColor: '#f1f5f9', color: '#475569', padding: '5px 12px', borderRadius: '20px', fontWeight: 'bold', fontSize: '11px' };
        }
    };

    if (loading) return <div style={styles.loading}>Cargando información...</div>;
    if (error) return <div style={styles.errorBox}>{error}</div>;

    return (
        <div style={styles.container}>
            <header style={styles.header}>
                <h1 style={styles.headerTitle}>Gestión de Suscripción & Finanzas</h1>
                <p style={styles.headerSubtitle}>Administración del Tenant: {info?.clinica_nombre}</p>
            </header>

            <div style={styles.topGrid}>
                {/* Card de Saldo */}
                <div style={styles.cardBalance}>
                    <p style={styles.balanceLabel}>SALDO DISPONIBLE</p>
                    <h2 style={styles.balanceValue}>{info?.saldo?.toFixed(2)} BOB</h2>
                    <form onSubmit={handleCargarSaldo} style={styles.chargeForm}>
                        <input 
                            type="number" 
                            placeholder="Monto" 
                            value={montoCarga}
                            onChange={(e) => setMontoCarga(e.target.value)}
                            style={styles.inputCharge}
                        />
                        <button type="submit" disabled={cargandoSaldo} style={styles.btnCharge}>
                            {cargandoSaldo ? '...' : 'CARGAR'}
                        </button>
                    </form>
                </div>

                {/* Card de Plan */}
                <div style={styles.cardPlan}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div>
                            <p style={styles.balanceLabel}>PLAN ACTUAL</p>
                            <h2 style={{ margin: '5px 0', fontSize: '24px', fontWeight: '800' }}>{info?.plan_nombre}</h2>
                        </div>
                        <span style={getBadgeStyle(info?.estado)}>{info?.estado}</span>
                    </div>
                    <p style={{ margin: '10px 0 0 0', fontSize: '12px', color: '#94a3b8' }}>
                        Registrado el: {new Date(info?.fecha_creacion).toLocaleDateString()}
                    </p>
                </div>
            </div>

            <div style={styles.mainGrid}>
                <div style={{ ...styles.card, gridColumn: 'span 2' }}>
                    <h3 style={styles.sectionTitle}>Historial de Facturación</h3>
                    <div style={{ overflowX: 'auto' }}>
                        <table style={styles.table}>
                            <thead>
                                <tr style={styles.tableHead}>
                                    <th style={styles.th}>FECHA</th>
                                    <th style={styles.th}>DESCRIPCIÓN</th>
                                    <th style={styles.th}>MÉTODO</th>
                                    <th style={styles.th}>MONTO</th>
                                </tr>
                            </thead>
                            <tbody>
                                {transacciones.length > 0 ? transacciones.map(t => (
                                    <tr key={t.id} style={styles.tr}>
                                        <td style={styles.td}>{t.fecha_formateada}</td>
                                        <td style={styles.td}>{t.descripcion}</td>
                                        <td style={styles.td}>
                                            <span style={styles.badgeMethod}>{t.metodo_pago}</span>
                                        </td>
                                        <td style={{ ...styles.td, fontWeight: 'bold', color: t.tipo === 'CARGA' ? '#16a34a' : '#dc2626' }}>
                                            {t.tipo === 'CARGA' ? '+' : '-'}{t.monto} BOB
                                        </td>
                                    </tr>
                                )) : (
                                    <tr><td colSpan="4" style={{ textAlign: 'center', padding: '20px', color: '#94a3b8' }}>Sin transacciones recientes.</td></tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div style={styles.card}>
                    <h3 style={styles.sectionTitle}>Uso de Recursos</h3>
                    <div style={styles.usageItem}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                            <span style={styles.usageLabel}>Pacientes</span>
                            <span style={styles.usageValue}>{info?.uso?.pacientes_actuales} / {info?.uso?.pacientes_limite}</span>
                        </div>
                        <div style={styles.progressBg}><div style={{ ...styles.progressFill, width: '10%', backgroundColor: '#2563eb' }} /></div>
                    </div>
                    <div style={styles.usageItem}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                            <span style={styles.usageLabel}>Especialistas</span>
                            <span style={styles.usageValue}>{info?.uso?.psicologos_actuales} / {info?.uso?.psicologos_limite}</span>
                        </div>
                        <div style={styles.progressBg}><div style={{ ...styles.progressFill, width: '20%', backgroundColor: '#16a34a' }} /></div>
                    </div>

                    <h3 style={{ ...styles.sectionTitle, marginTop: '30px' }}>Acciones Rápidas</h3>
                    <button onClick={() => navigate('/configuracion-clinica')} style={styles.btnAction}>⚙️ Configuración del Tenant</button>
                    <button onClick={() => navigate('/bitacora')} style={styles.btnAction}>📜 Ver Bitácora de Auditoría</button>
                </div>
            </div>
        </div>
    );
};

const styles = {
    container: { padding: '32px', maxWidth: '1200px', margin: '0 auto', backgroundColor: '#f1f5f9', minHeight: '100vh' },
    header: { marginBottom: '32px' },
    headerTitle: { margin: 0, fontSize: '28px', color: '#0f172a', fontWeight: '800' },
    headerSubtitle: { margin: 0, color: '#64748b', fontSize: '16px' },
    topGrid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' },
    cardBalance: { background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)', padding: '30px', borderRadius: '20px', color: 'white', boxShadow: '0 10px 20px rgba(0,0,0,0.1)' },
    balanceLabel: { margin: 0, fontSize: '11px', fontWeight: '900', color: '#94a3b8', letterSpacing: '1px' },
    balanceValue: { margin: '10px 0 20px 0', fontSize: '36px', fontWeight: '800' },
    chargeForm: { display: 'flex', gap: '10px' },
    inputCharge: { backgroundColor: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', padding: '10px', borderRadius: '8px', color: 'white', flex: 1, outline: 'none' },
    btnCharge: { backgroundColor: '#2563eb', color: 'white', border: 'none', padding: '0 20px', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer' },
    cardPlan: { backgroundColor: 'white', padding: '30px', borderRadius: '20px', boxShadow: '0 4px 15px rgba(0,0,0,0.05)', border: '1px solid #e2e8f0' },
    mainGrid: { display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' },
    card: { backgroundColor: 'white', padding: '24px', borderRadius: '20px', boxShadow: '0 4px 15px rgba(0,0,0,0.05)', border: '1px solid #e2e8f0' },
    sectionTitle: { margin: '0 0 20px 0', fontSize: '18px', color: '#1e293b', fontWeight: '700' },
    table: { width: '100%', borderCollapse: 'collapse' },
    tableHead: { borderBottom: '2px solid #f1f5f9' },
    th: { textAlign: 'left', padding: '12px', fontSize: '11px', color: '#64748b', fontWeight: 'bold', textTransform: 'uppercase' },
    tr: { borderBottom: '1px solid #f8fafc' },
    td: { padding: '12px', fontSize: '13px', color: '#334155' },
    badgeMethod: { backgroundColor: '#f1f5f9', color: '#475569', padding: '3px 8px', borderRadius: '6px', fontSize: '10px', fontWeight: 'bold' },
    usageItem: { marginBottom: '20px' },
    usageLabel: { fontSize: '13px', color: '#64748b', fontWeight: '600' },
    usageValue: { fontSize: '13px', color: '#1e293b', fontWeight: 'bold' },
    progressBg: { height: '6px', backgroundColor: '#f1f5f9', borderRadius: '3px', overflow: 'hidden' },
    progressFill: { height: '100%', borderRadius: '3px' },
    btnAction: { width: '100%', padding: '12px', backgroundColor: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '10px', textAlign: 'left', marginBottom: '10px', cursor: 'pointer', fontWeight: '600', color: '#334155', transition: 'all 0.2s' },
    loading: { textAlign: 'center', padding: '100px', fontSize: '18px', color: '#64748b' },
    errorBox: { padding: '20px', backgroundColor: '#fef2f2', color: '#dc2626', border: '1px solid #fee2e2', borderRadius: '12px', margin: '32px' }
};

export default SuscripcionInfo;
