// ==============================================================================
// [SPRINT 2] Componente Toast — Notificaciones visuales inline (RF-09 parcial)
// Sustituye temporalmente las Push Notifications hasta integrar Firebase.
// ==============================================================================
import React, { useEffect, useState } from 'react';

const TOAST_TYPES = {
    success: { bg: '#10b981', icon: '✅' },
    error: { bg: '#ef4444', icon: '❌' },
    warning: { bg: '#f59e0b', icon: '⚠️' },
    info: { bg: '#3b82f6', icon: 'ℹ️' },
};

const Toast = ({ message, type = 'info', duration = 4000, onClose }) => {
    const [visible, setVisible] = useState(true);
    const config = TOAST_TYPES[type] || TOAST_TYPES.info;

    useEffect(() => {
        const timer = setTimeout(() => {
            setVisible(false);
            if (onClose) onClose();
        }, duration);
        return () => clearTimeout(timer);
    }, [duration, onClose]);

    if (!visible) return null;

    return (
        <div style={{
            position: 'fixed',
            top: '24px',
            right: '24px',
            backgroundColor: config.bg,
            color: 'white',
            padding: '16px 24px',
            borderRadius: '16px',
            boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
            zIndex: 10000,
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            fontSize: '14px',
            fontWeight: '600',
            fontFamily: '"Inter", sans-serif',
            animation: 'slideInRight 0.4s cubic-bezier(0.16,1,0.3,1)',
            maxWidth: '420px',
        }}>
            <span style={{ fontSize: '18px' }}>{config.icon}</span>
            <span>{message}</span>
            <button
                onClick={() => { setVisible(false); if (onClose) onClose(); }}
                style={{
                    background: 'rgba(255,255,255,0.2)',
                    border: 'none',
                    color: 'white',
                    cursor: 'pointer',
                    borderRadius: '50%',
                    width: '24px',
                    height: '24px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginLeft: '8px',
                    fontSize: '12px',
                }}
            >✕</button>
        </div>
    );
};

/**
 * Hook para manejar toasts de forma declarativa.
 * Uso: const { toast, showToast } = useToast();
 */
export const useToast = () => {
    const [toasts, setToasts] = useState([]);

    const showToast = (message, type = 'info', duration = 4000) => {
        const id = Date.now();
        setToasts(prev => [...prev, { id, message, type, duration }]);
    };

    const removeToast = (id) => {
        setToasts(prev => prev.filter(t => t.id !== id));
    };

    const ToastContainer = () => (
        <>
            {toasts.map((t, idx) => (
                <div key={t.id} style={{ position: 'fixed', top: `${24 + idx * 80}px`, right: '24px', zIndex: 10000 }}>
                    <Toast
                        message={t.message}
                        type={t.type}
                        duration={t.duration}
                        onClose={() => removeToast(t.id)}
                    />
                </div>
            ))}
        </>
    );

    return { showToast, ToastContainer };
};

export default Toast;
