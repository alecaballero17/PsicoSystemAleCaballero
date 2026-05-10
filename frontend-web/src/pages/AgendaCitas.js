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
        <div className="agenda-container" style={{ padding: '20px', backgroundColor: '#f1f5f9', minHeight: '100vh', fontFamily: '"Inter", sans-serif' }}>
            <ToastContainer />

            {/* Header */}
            <div className="agenda-header" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
                <div>
                    <h1 style={styles.pageTitle}>📅 Agenda Profesional</h1>
                    <p style={styles.pageSubtitle}>
                        Gestión de horarios y citas sincronizada
                    </p>
                </div>
                <div className="agenda-actions" style={{ display: 'flex', gap: '12px' }}>
                    <button onClick={fetchCitas} style={styles.btnSecondary} disabled={loading}>
                        🔄 {loading ? 'Cargando...' : 'Actualizar'}
                    </button>
                    <button
                        onClick={() => navigate('/gestion-citas')}
                        style={styles.btnPrimary}
                    >
                        + Nueva Cita
                    </button>
                </div>
            </div>

            {/* Calendario */}
            <div style={styles.calendarWrapper}>
                {loading ? (
                    <div style={styles.loadingState}>
                        <div style={styles.spinner} />
                        <p>Sincronizando agenda con el servidor...</p>
                    </div>
                ) : error ? (
                    <div style={{ textAlign: 'center', padding: '60px' }}>
                        <div style={{ fontSize: '48px', marginBottom: '20px' }}>❌</div>
                        <h2 style={{ color: '#0f172a' }}>{error}</h2>
                        <button onClick={fetchCitas} style={{ ...styles.btnPrimary, marginTop: '20px' }}>
                            Reintentar Conexión
                        </button>
                    </div>
                ) : (
                    <Calendar
                        localizer={localizer}
                        events={citas}
                        startAccessor="start"
                        endAccessor="end"
                        style={{ height: 700 }}
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
                        min={new Date(2026, 0, 1, 7, 0)}
                        max={new Date(2026, 0, 1, 21, 0)}
                        step={30}
                        timeslots={2}
                        popup
                        toolbar={true}
                    />
                )}
            </div>
        </div>
    );
};

// ==============================================================================
// ESTILOS — Sistema de diseño consistente con Sprint 1
// ==============================================================================
const styles = {
    pageContainer: {
        padding: 'clamp(16px, 5vw, 40px)',
        backgroundColor: '#f1f5f9',
        minHeight: '100vh',
        fontFamily: '"Inter", sans-serif',
    },
    headerSection: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '24px',
    },
    pageTitle: {
        fontSize: '28px',
        fontWeight: '800',
        color: '#0f172a',
        margin: 0,
    },
    pageSubtitle: {
        fontSize: '14px',
        color: '#64748b',
        marginTop: '4px',
    },
    headerActions: {
        display: 'flex',
        gap: '12px',
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
        transition: 'all 0.2s',
        boxShadow: '0 4px 12px rgba(37,99,235,0.3)',
    },
    btnSecondary: {
        backgroundColor: 'white',
        color: '#475569',
        padding: '12px 20px',
        borderRadius: '12px',
        border: '1px solid #e2e8f0',
        fontWeight: '600',
        fontSize: '14px',
        cursor: 'pointer',
    },
    legendBar: {
        display: 'flex',
        gap: '24px',
        alignItems: 'center',
        padding: '16px 24px',
        backgroundColor: 'white',
        borderRadius: '16px',
        border: '1px solid #e2e8f0',
        marginBottom: '24px',
    },
    legendItem: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
    },
    legendDot: {
        width: '12px',
        height: '12px',
        borderRadius: '50%',
    },
    legendText: {
        fontSize: '13px',
        fontWeight: '600',
        color: '#475569',
        textTransform: 'capitalize',
    },
    legendInfo: {
        fontSize: '13px',
        color: '#64748b',
        marginLeft: 'auto',
    },
    calendarWrapper: {
        backgroundColor: 'white',
        borderRadius: '20px',
        border: '1px solid #e2e8f0',
        padding: '24px',
        boxShadow: '0 4px 24px rgba(0,0,0,0.06)',
    },
    loadingState: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '500px',
        color: '#64748b',
    },
    spinner: {
        width: '48px',
        height: '48px',
        border: '4px solid #e2e8f0',
        borderTopColor: '#3b82f6',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite',
        marginBottom: '16px',
    },
};

export default AgendaCitas;
