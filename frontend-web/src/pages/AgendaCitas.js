// ==============================================================================
// [SPRINT 2 - RF-08 / CU14] Agenda Dinámica — Calendario Interactivo
// Visualización profesional de citas con react-big-calendar.
// Sincronizado con el backend Django en tiempo real.
// ==============================================================================
import React, { useEffect, useState, useCallback } from 'react';
import { Calendar, momentLocalizer } from 'react-big-calendar';
import moment from 'moment';
import 'moment/locale/es';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import citaService from '../services/citaService';
import { useToast } from '../components/Toast';

moment.locale('es');
const localizer = momentLocalizer(moment);

// Traducciones al español para react-big-calendar
const MESSAGES_ES = {
    allDay: 'Todo el día',
    previous: '← Anterior',
    next: 'Siguiente →',
    today: 'Hoy',
    month: 'Mes',
    week: 'Semana',
    day: 'Día',
    agenda: 'Agenda',
    date: 'Fecha',
    time: 'Hora',
    event: 'Cita',
    noEventsInRange: 'No hay citas programadas en este período.',
    showMore: (total) => `+ ${total} más`,
};

// Colores por estado de cita
const ESTADO_COLORS = {
    PENDIENTE: { bg: '#3b82f6', border: '#2563eb' },
    COMPLETADA: { bg: '#10b981', border: '#059669' },
    CANCELADA: { bg: '#ef4444', border: '#dc2626' },
};

const AgendaCitas = () => {
    const navigate = useNavigate();
    const { user } = useAuth();
    const { showToast, ToastContainer } = useToast();
    const [citas, setCitas] = useState([]);
    const [loading, setLoading] = useState(true);
    const [currentDate, setCurrentDate] = useState(new Date());
    const [currentView, setCurrentView] = useState('week');
    const [error, setError] = useState(null);

    const fetchCitas = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await citaService.getCitas();
            const eventos = (Array.isArray(data) ? data : [])
                .filter(cita => cita.fecha_hora) // Ignorar citas sin fecha
                .map(cita => {
                    const start = new Date(cita.fecha_hora);
                    if (isNaN(start.getTime())) return null; // Ignorar fechas inválidas

                    return {
                        id: cita.id,
                        title: `${cita.paciente_nombre || 'Paciente'} — ${cita.psicologo_nombre || 'Dr.'}`,
                        start: start,
                        end: new Date(start.getTime() + 60 * 60 * 1000), // +1 hora
                        estado: cita.estado,
                        paciente: cita.paciente_nombre,
                        psicologo: cita.psicologo_nombre,
                        motivo: cita.motivo,
                        resource: cita,
                    };
                })
                .filter(e => e !== null);
            setCitas(eventos);
        } catch (err) {
            console.error("Error en Agenda:", err);
            const msg = err.code === 'ECONNABORTED' 
                ? 'El servidor tardó demasiado en responder (Timeout).' 
                : 'Error al conectar con el servidor. Verifique que el backend esté corriendo.';
            setError(msg);
            showToast(msg, 'error');
        } finally {
            setLoading(false);
        }
    }, [showToast]);

    useEffect(() => {
        fetchCitas();
    }, [fetchCitas]);

    const eventStyleGetter = (event) => {
        const colors = ESTADO_COLORS[event.estado] || ESTADO_COLORS.PENDIENTE;
        return {
            style: {
                backgroundColor: colors.bg,
                borderLeft: `4px solid ${colors.border}`,
                borderRadius: '8px',
                color: 'white',
                fontSize: '12px',
                fontWeight: '600',
                padding: '4px 8px',
                border: 'none',
                boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
            },
        };
    };

    const handleSelectEvent = (event) => {
        navigate('/gestion-citas', { state: { citaId: event.id } });
    };

    const handleSelectSlot = (slotInfo) => {
        navigate('/gestion-citas', {
            state: { preselectedDate: slotInfo.start.toISOString() }
        });
    };

    return (
        <div className="agenda-container" style={styles.pageContainer}>
            <ToastContainer />

            {/* Header Glassmorphism Card */}
            <div style={styles.headerCard}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <div style={styles.iconCircle}>📅</div>
                    <div>
                        <h1 style={styles.pageTitle}>Agenda Profesional</h1>
                        <p style={styles.pageSubtitle}>
                            Gestión centralizada de citas y disponibilidad para {tenant?.nombre}
                        </p>
                    </div>
                </div>
                
                <div style={{ display: 'flex', gap: '12px' }}>
                    <button 
                        onClick={() => setCurrentDate(new Date())} 
                        style={styles.btnToday}
                    >
                        Hoy
                    </button>
                    <button onClick={fetchCitas} style={styles.btnSecondary} disabled={loading}>
                        {loading ? '🔄 Sincronizando...' : '🔄 Actualizar'}
                    </button>
                    <button
                        onClick={() => navigate('/gestion-citas')}
                        style={styles.btnPrimary}
                    >
                        + Nueva Cita
                    </button>
                </div>
            </div>

            {/* Leyenda de Estados */}
            <div style={styles.legendBar}>
                <div style={styles.legendItem}>
                    <div style={{ ...styles.legendDot, backgroundColor: '#3b82f6' }}></div>
                    <span style={styles.legendText}>Pendientes</span>
                </div>
                <div style={styles.legendItem}>
                    <div style={{ ...styles.legendDot, backgroundColor: '#10b981' }}></div>
                    <span style={styles.legendText}>Completadas</span>
                </div>
                <div style={styles.legendItem}>
                    <div style={{ ...styles.legendDot, backgroundColor: '#ef4444' }}></div>
                    <span style={styles.legendText}>Canceladas</span>
                </div>
                <div style={{ marginLeft: 'auto', fontSize: '12px', color: '#64748b', fontWeight: '600' }}>
                    Tip: Haz clic en una cita para ver detalles o reprogramar.
                </div>
            </div>

            {/* Calendario Container */}
            <div style={styles.calendarWrapper}>
                {loading ? (
                    <div style={styles.loadingState}>
                        <div className="premium-spinner" />
                        <p style={{ marginTop: '20px', fontWeight: '600' }}>Sincronizando agenda con el servidor...</p>
                    </div>
                ) : error ? (
                    <div style={styles.errorState}>
                        <div style={{ fontSize: '64px', marginBottom: '20px' }}>⚠️</div>
                        <h2 style={{ color: '#0f172a', fontWeight: '800' }}>No se pudo cargar la agenda</h2>
                        <p style={{ color: '#64748b', maxWidth: '400px', margin: '10px auto' }}>{error}</p>
                        <button onClick={fetchCitas} style={styles.btnPrimary}>
                            Reintentar Conexión
                        </button>
                    </div>
                ) : (
                    <Calendar
                        localizer={localizer}
                        events={citas}
                        startAccessor="start"
                        endAccessor="end"
                        style={{ height: 'calc(100vh - 350px)', minHeight: '600px' }}
                        views={['month', 'week', 'day', 'agenda']}
                        defaultView="week"
                        view={currentView}
                        onView={setCurrentView}
                        date={currentDate}
                        onNavigate={setCurrentDate}
                        eventPropGetter={eventStyleGetter}
                        onSelectEvent={handleSelectEvent}
                        onSelectSlot={handleSelectSlot}
                        selectable
                        messages={MESSAGES_ES}
                        step={30}
                        timeslots={2}
                        popup
                        toolbar={true}
                    />
                )}
            </div>

            <style>{`
                @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
                .premium-spinner {
                    width: 50px; height: 50px;
                    border: 4px solid #f1f5f9;
                    border-top: 4px solid #2563eb;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                }
                .rbc-calendar { font-family: 'Inter', sans-serif !important; border: none !important; }
                .rbc-header { padding: 12px !important; font-weight: 700 !important; color: #475569 !important; background: #f8fafc !important; border-bottom: 2px solid #e2e8f0 !important; }
                .rbc-event { padding: 5px 10px !important; }
                .rbc-today { background-color: #eff6ff !important; }
            `}</style>
        </div>
    );
};

const styles = {
    pageContainer: {
        padding: '24px',
        backgroundColor: '#f8fafc',
        minHeight: '100vh',
    },
    headerCard: {
        background: 'rgba(255, 255, 255, 0.8)',
        backdropFilter: 'blur(10px)',
        borderRadius: '24px',
        padding: '24px 32px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        boxShadow: '0 4px 20px rgba(0,0,0,0.05)',
        border: '1px solid white',
        marginBottom: '24px'
    },
    iconCircle: {
        width: '56px',
        height: '56px',
        borderRadius: '16px',
        backgroundColor: '#eff6ff',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '24px',
        boxShadow: '0 4px 12px rgba(37,99,235,0.1)'
    },
    pageTitle: {
        fontSize: '24px',
        fontWeight: '900',
        color: '#0f172a',
        margin: 0,
        letterSpacing: '-0.5px'
    },
    pageSubtitle: {
        fontSize: '14px',
        color: '#64748b',
        margin: '4px 0 0 0',
        fontWeight: '500'
    },
    btnPrimary: {
        backgroundColor: '#2563eb',
        color: 'white',
        padding: '12px 24px',
        borderRadius: '12px',
        border: 'none',
        fontWeight: '700',
        fontSize: '14px',
        cursor: 'pointer',
        boxShadow: '0 10px 15px -3px rgba(37,99,235,0.3)',
        transition: 'all 0.2s'
    },
    btnSecondary: {
        backgroundColor: 'white',
        color: '#475569',
        padding: '12px 20px',
        borderRadius: '12px',
        border: '1px solid #e2e8f0',
        fontWeight: '700',
        fontSize: '14px',
        cursor: 'pointer',
        boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
    },
    btnToday: {
        backgroundColor: '#f1f5f9',
        color: '#1e293b',
        padding: '12px 20px',
        borderRadius: '12px',
        border: 'none',
        fontWeight: '700',
        fontSize: '14px',
        cursor: 'pointer'
    },
    legendBar: {
        display: 'flex',
        gap: '24px',
        padding: '12px 24px',
        marginBottom: '24px'
    },
    legendItem: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
    },
    legendDot: {
        width: '10px',
        height: '10px',
        borderRadius: '50%'
    },
    legendText: {
        fontSize: '12px',
        fontWeight: '700',
        color: '#475569'
    },
    calendarWrapper: {
        backgroundColor: 'white',
        borderRadius: '24px',
        padding: '24px',
        boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)',
        border: '1px solid #f1f5f9'
    },
    loadingState: {
        height: '500px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#64748b'
    },
    errorState: {
        height: '500px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center'
    }
};

export default AgendaCitas;
