import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import apiClient from '../api/axiosConfig';

const Navbar = () => {
    const { user, logout, tenant } = useAuth();
    const [notificaciones, setNotificaciones] = useState([]);
    const [showNotifs, setShowNotifs] = useState(false);
    const alertedNotifsRef = React.useRef(new Set());

    useEffect(() => {
        if ("Notification" in window && Notification.permission !== "granted" && Notification.permission !== "denied") {
            Notification.requestPermission();
        }
    }, []);

    const fetchNotificaciones = async () => {
        if (!user) return;
        try {
            const res = await apiClient.get('notificaciones/');
            const nuevasNotificaciones = res.data;
            setNotificaciones(nuevasNotificaciones);

            // Web Push Notifications reales
            if ("Notification" in window && Notification.permission === "granted") {
                nuevasNotificaciones.forEach(n => {
                    if (!n.leido && !alertedNotifsRef.current.has(n.id)) {
                        new Notification(n.titulo || "Nueva Notificación", {
                            body: n.mensaje,
                            icon: "/favicon.ico"
                        });
                        alertedNotifsRef.current.add(n.id);
                    }
                });
            } else {
                // Registrar IDs para evitar alertas si dan permiso después
                nuevasNotificaciones.forEach(n => alertedNotifsRef.current.add(n.id));
            }

        } catch (error) {
            console.error("Error al obtener notificaciones:", error);
        }
    };

    useEffect(() => {
        fetchNotificaciones();
        // Poll every 15 seconds
        const interval = setInterval(fetchNotificaciones, 15000);
        return () => clearInterval(interval);
    }, [user]);

    const marcarLeidas = async () => {
        try {
            await apiClient.patch('notificaciones/');
            setNotificaciones(notificaciones.map(n => ({ ...n, leido: true })));
        } catch (error) {
            console.error("Error al marcar como leídas:", error);
        }
    };

    return (
        <nav style={{ padding: '10px 20px', background: '#1a2233', color: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            {/* [ALINEACIÓN RNF-05] - Identidad de marca unificada: Diferenciación visual entre el Proveedor SaaS (PsicoSystem) y el Tenant activo (RF-29). */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ width: '32px', height: '32px', background: '#2563eb', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '900', fontSize: '14px' }}>
                    PS
                </div>
                <h2 style={{ margin: 0, fontSize: '18px', letterSpacing: '1px', fontWeight: '800' }}>PSICOSYSTEM</h2>
            </div>
            {user && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <div style={{ position: 'relative', cursor: 'pointer' }} onClick={() => setShowNotifs(!showNotifs)}>
                        <span style={{ fontSize: '20px' }}>🔔</span>
                        {notificaciones.filter(n => !n.leido).length > 0 && (
                            <span style={{ position: 'absolute', top: '-5px', right: '-5px', background: 'red', color: 'white', borderRadius: '50%', padding: '2px 6px', fontSize: '10px', fontWeight: 'bold' }}>
                                {notificaciones.filter(n => !n.leido).length}
                            </span>
                        )}
                        {showNotifs && (
                            <div style={{ position: 'absolute', top: '35px', right: '0', background: 'white', color: 'black', width: '300px', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', zIndex: 1000, maxHeight: '400px', overflowY: 'auto' }}>
                                <div style={{ padding: '10px', borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <h4 style={{ margin: 0 }}>Notificaciones</h4>
                                    <button onClick={marcarLeidas} style={{ background: 'none', border: 'none', color: '#2563eb', cursor: 'pointer', fontSize: '12px' }}>Marcar todas leídas</button>
                                </div>
                                {notificaciones.length === 0 ? (
                                    <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>No hay notificaciones</div>
                                ) : (
                                    notificaciones.map(n => (
                                        <div key={n.id} style={{ padding: '10px', borderBottom: '1px solid #eee', background: n.leido ? 'white' : '#f0f9ff' }}>
                                            <div style={{ fontWeight: 'bold', fontSize: '14px' }}>{n.titulo}</div>
                                            <div style={{ fontSize: '12px', color: '#555' }}>{n.mensaje}</div>
                                            <div style={{ fontSize: '10px', color: '#999', marginTop: '4px' }}>{new Date(n.fecha).toLocaleString()}</div>
                                        </div>
                                    ))
                                )}
                            </div>
                        )}
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', justifyContent: 'center' }}>
                        <span style={{ color: '#e2e8f0', fontSize: '14px', fontWeight: 'bold' }}>
                            🏥 {tenant?.nombre || "Cargando Clínica..."}
                        </span>
                        <span style={{ color: '#94a3b8', fontSize: '12px' }}>
                            👤 {user.name} ({user.role})
                        </span>
                    </div>
                    <button onClick={logout} style={{ padding: '8px 16px', background: '#dc2626', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold', transition: 'background 0.2s' }} onMouseOver={e => e.target.style.background = '#b91c1c'} onMouseOut={e => e.target.style.background = '#dc2626'}>
                        Cerrar Sesión
                    </button>
                </div>
            )}
        </nav>
    );
};

export default Navbar;