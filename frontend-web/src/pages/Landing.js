// [CIERRE SPRINT 1] Flujo SaaS integrado: Landing Page pública (Requerimiento 3.2).
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const Landing = () => {
    const navigate = useNavigate();
    const { user } = useAuth();

    // Redirección si ya está autenticado (RBAC T018)
    useEffect(() => {
        if (user) {
            navigate('/dashboard');
        }
    }, [user, navigate]);

    return (
        <div style={styles.container}>
            <header style={styles.header}>
                <div style={styles.logo}>⚕️ PsicoSystem B2B</div>
                <div>
                    <button style={styles.btnLogin} onClick={() => navigate('/login')}>
                        Iniciar Sesión
                    </button>
                    <button style={styles.btnPrimary} onClick={() => navigate('/registro-clinica')}>
                        Registra tu Clínica
                    </button>
                </div>
            </header>

            <main style={styles.hero}>
                <h1 style={styles.title}>Transforma la Gestión de tu Centro Psicológico</h1>
                <p style={styles.subtitle}>
                    Automatiza el registro de pacientes, reduce costos operativos y elimina la 
                    burocracia de la gestión de turnos con nuestro entorno aislado SaaS.
                </p>
                <div style={styles.ctaContainer}>
                    <button style={styles.btnCta} onClick={() => navigate('/registro-clinica')}>
                        ¿Administras un Centro Psicológico? Registra tu Clínica aquí.
                    </button>
                </div>
            </main>

            <section style={styles.features}>
                <div style={styles.featureCard}>
                    <div style={styles.icon}>⏱️</div>
                    <h3>Ahorro de Tiempo</h3>
                    <p>Reducción de burocracia documental y automatización en la captura de métricas del paciente.</p>
                </div>
                <div style={styles.featureCard}>
                    <div style={styles.icon}>🤖</div>
                    <h3>Menos Esfuerzo Humano</h3>
                    <p>Automatización de flujos repetitivos y recordatorios para reducir la carga laboral del personal.</p>
                </div>
                <div style={styles.featureCard}>
                    <div style={styles.icon}>💰</div>
                    <h3>Reducción de Costos</h3>
                    <p>Ahorro sustancial en papelería, impresión, archiveros físicos y mobiliario de almacenamiento.</p>
                </div>
            </section>
        </div>
    );
};

const styles = {
    container: {
        fontFamily: "'Inter', sans-serif",
        backgroundColor: '#f8fafc',
        minHeight: '100vh',
    },
    header: {
        display: 'flex',
        justifyContent: 'space-between',
        padding: '24px 40px',
        backgroundColor: 'white',
        boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
        alignItems: 'center'
    },
    logo: {
        fontSize: '24px',
        fontWeight: 'bold',
        color: '#0f172a'
    },
    btnLogin: {
        background: 'none',
        border: 'none',
        color: '#475569',
        fontWeight: 'bold',
        cursor: 'pointer',
        marginRight: '20px',
        fontSize: '16px'
    },
    btnPrimary: {
        backgroundColor: '#2563eb',
        color: 'white',
        border: 'none',
        padding: '10px 20px',
        borderRadius: '8px',
        cursor: 'pointer',
        fontWeight: 'bold'
    },
    hero: {
        textAlign: 'center',
        padding: '80px 20px',
    },
    title: {
        fontSize: '48px',
        color: '#0f172a',
        marginBottom: '20px'
    },
    subtitle: {
        fontSize: '20px',
        color: '#64748b',
        maxWidth: '700px',
        margin: '0 auto',
        lineHeight: '1.6'
    },
    ctaContainer: {
        marginTop: '40px'
    },
    btnCta: {
        backgroundColor: '#16a34a',
        color: 'white',
        border: 'none',
        padding: '16px 32px',
        borderRadius: '12px',
        fontSize: '18px',
        fontWeight: 'bold',
        cursor: 'pointer',
        boxShadow: '0 10px 15px -3px rgba(22, 163, 74, 0.4)'
    },
    features: {
        display: 'flex',
        justifyContent: 'center',
        gap: '40px',
        padding: '60px 40px',
        flexWrap: 'wrap'
    },
    featureCard: {
        backgroundColor: 'white',
        padding: '40px',
        borderRadius: '16px',
        width: '300px',
        textAlign: 'center',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
    },
    icon: {
        fontSize: '48px',
        marginBottom: '20px'
    }
};

export default Landing;
