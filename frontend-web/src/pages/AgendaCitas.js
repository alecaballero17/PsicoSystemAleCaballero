import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/axiosConfig';

const AgendaCitas = () => {
    const navigate = useNavigate();
    const [citas, setCitas] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchCitas();
    }, []);

    const fetchCitas = async () => {
        try {
            const response = await apiClient.get('logistica/gestion/');
            setCitas(response.data);
        } catch (err) {
            console.error("Error al cargar citas", err);
        } finally {
            setLoading(false);
        }
    };

    const enviarRecordatorio = async (citaId) => {
        try {
            await apiClient.post(`logistica/gestion/${citaId}/enviar_recordatorio/`);
            if ("Notification" in window) {
                if (Notification.permission === "granted") {
                    new Notification("PsicoSystem Recordatorio", { body: "Se ha enviado un correo de recordatorio al paciente.", icon: "/favicon.ico" });
                } else if (Notification.permission !== "denied") {
                    Notification.requestPermission().then(permission => {
                        if (permission === "granted") {
                            new Notification("PsicoSystem Recordatorio", { body: "Se ha enviado un correo de recordatorio al paciente.", icon: "/favicon.ico" });
                        }
                    });
                }
            }
            alert("Recordatorio enviado correctamente al paciente.");
        } catch (err) {
            alert("Error al enviar recordatorio.");
        }
    };

    const handleCancelar = async (citaId) => {
        if (window.confirm("¿Está seguro de cancelar esta cita? Se enviará una notificación al paciente.")) {
            try {
                await apiClient.post(`logistica/gestion/${citaId}/cancelar/`);
                if ("Notification" in window) {
                    if (Notification.permission === "granted") {
                        new Notification("PsicoSystem Alerta", { body: "La cita ha sido cancelada exitosamente.", icon: "/favicon.ico" });
                    } else if (Notification.permission !== "denied") {
                        Notification.requestPermission().then(permission => {
                            if (permission === "granted") {
                                new Notification("PsicoSystem Alerta", { body: "La cita ha sido cancelada exitosamente.", icon: "/favicon.ico" });
                            }
                        });
                    }
                }
                alert("Cita cancelada correctamente.");
                fetchCitas();
            } catch (err) {
                alert("Error al cancelar la cita.");
            }
        }
    };

    return (
        <div style={styles.container}>
            <header style={styles.header}>
                <h2 style={styles.title}>AGENDA DE CITAS (CU14/15)</h2>
                <button 
                    style={styles.btnPrimary}
                    onClick={() => navigate('/registro-cita')}
                >
                    + NUEVA CITA
                </button>
            </header>

            {loading ? (
                <p>Cargando agenda...</p>
            ) : (
                <div style={styles.grid}>
                    {citas.map(cita => (
                        <div key={cita.id} style={styles.card}>
                            <div style={styles.cardHeader}>
                                <span style={styles.fecha}>{new Date(cita.fecha_hora).toLocaleDateString()}</span>
                                <span style={styles.hora}>{new Date(cita.fecha_hora).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                            </div>
                            <h3 style={styles.paciente}>{cita.paciente_nombre || "Paciente"}</h3>
                            <p style={styles.motivo}>{cita.motivo || "Sin motivo especificado"}</p>
                            <div style={styles.footer}>
                                <button 
                                    style={styles.btnReminder}
                                    onClick={() => enviarRecordatorio(cita.id)}
                                >
                                    🔔 RECORDATORIO
                                </button>
                                <button 
                                    style={styles.btnCancel}
                                    onClick={() => handleCancelar(cita.id)}
                                    disabled={cita.estado === 'CANCELADA'}
                                >
                                    ❌ CANCELAR
                                </button>
                                <span style={styles.estado}>{cita.estado}</span>
                            </div>
                        </div>
                    ))}
                    {citas.length === 0 && <p>No hay citas programadas.</p>}
                </div>
            )}
        </div>
    );
};

const styles = {
    container: { padding: '40px', backgroundColor: '#f8fafc', minHeight: '100vh' },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' },
    title: { margin: 0, color: '#0f172a', fontSize: '24px', fontWeight: 'bold' },
    btnPrimary: { padding: '12px 24px', backgroundColor: '#16a34a', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' },
    grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' },
    card: { backgroundColor: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' },
    cardHeader: { display: 'flex', justifyContent: 'space-between', marginBottom: '10px' },
    fecha: { fontSize: '12px', color: '#64748b', fontWeight: 'bold' },
    hora: { fontSize: '12px', color: '#2563eb', fontWeight: 'bold' },
    paciente: { margin: '10px 0', fontSize: '18px', color: '#1e293b' },
    motivo: { fontSize: '14px', color: '#475569', marginBottom: '20px' },
    footer: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '10px' },
    btnReminder: { padding: '8px 12px', backgroundColor: '#f59e0b', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '11px', fontWeight: 'bold' },
    btnCancel: { padding: '8px 12px', backgroundColor: '#ef4444', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '11px', fontWeight: 'bold' },
    estado: { fontSize: '11px', color: '#10b981', fontWeight: 'bold', textTransform: 'uppercase' }
};

export default AgendaCitas;
