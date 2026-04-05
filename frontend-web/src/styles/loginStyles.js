// src/styles/loginStyles.js

export const loginStyles = {
    container: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        backgroundColor: '#f8fafc',
        fontFamily: '"Inter", sans-serif'
    },
    card: {
        backgroundColor: 'white',
        padding: '48px 40px',
        borderRadius: '24px',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        width: '100%',
        maxWidth: '400px',
        textAlign: 'center',
        border: '1px solid #f1f5f9'
    },
    logoIcon: {
        fontSize: '40px',
        marginBottom: '16px'
    },
    title: {
        color: '#1e293b',
        fontSize: '28px',
        fontWeight: '800',
        margin: '0 0 8px 0'
    },
    subtitle: {
        color: '#64748b',
        marginBottom: '32px',
        fontSize: '15px'
    },
    inputGroup: {
        textAlign: 'left',
        marginBottom: '20px'
    },
    label: {
        display: 'block',
        fontSize: '14px',
        fontWeight: '600',
        color: '#475569',
        marginBottom: '8px'
    },
    input: {
        width: '100%',
        padding: '12px 16px',
        borderRadius: '12px',
        border: '1px solid #e2e8f0',
        fontSize: '16px',
        boxSizing: 'border-box',
        backgroundColor: '#f8fafc'
    },
    button: {
        width: '100%',
        padding: '14px',
        color: 'white',
        border: 'none',
        borderRadius: '12px',
        fontSize: '16px',
        fontWeight: '700',
        cursor: 'pointer',
        marginTop: '10px',
        transition: 'all 0.2s'
    },
    footerText: {
        marginTop: '32px',
        fontSize: '12px',
        color: '#94a3b8',
        textTransform: 'uppercase',
        letterSpacing: '1px'
    }
};