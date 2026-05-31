// [ALINEACIÓN SPRINT 1 - T016/T017] - Gestión de perfiles administrativos y clínicos bajo aislamiento de Tenant (RF-29).
// [RF-04] Gestión de Personal Clínico. [RF-28] Control de Acceso (Solo ADMIN).
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/axiosConfig';

export const GestionPersonal = () => {
    const navigate = useNavigate();
    const [psicologos, setPsicologos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [showModal, setShowModal] = useState(false);
    const [showLimitModal, setShowLimitModal] = useState(false);
    const [limitMessage, setLimitMessage] = useState('');

    // Formulario de edición/creación
    const [formData, setFormData] = useState({
        id: null,
        username: '',
        email: '',
        password: '',
        password_confirm: '',
        rol: 'PSICOLOGO',
        especialidad: '',
        horario_atencion: '',
    });

    // Horarios interactivos
    const [diasPreset, setDiasPreset] = useState('Lunes a Viernes');
    const [selectedDays, setSelectedDays] = useState([]);
    const [horaInicio, setHoraInicio] = useState('08:00');
    const [horaFin, setHoraFin] = useState('16:00');

    const parseHorario = (str) => {
        let preset = 'Lunes a Viernes';
        let start = '08:00';
        let end = '16:00';
        let custom = [];

        if (!str) return { preset, start, end, custom };

        // Try parsing hours (e.g. 08:00 - 16:00)
        const hoursMatch = str.match(/(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})/);
        if (hoursMatch) {
            start = hoursMatch[1];
            end = hoursMatch[2];
        }

        // Try parsing days
        if (str.includes('Lunes a Viernes')) {
            preset = 'Lunes a Viernes';
        } else if (str.includes('Lunes a Sábado')) {
            preset = 'Lunes a Sábado';
        } else if (str.includes('Lunes a Domingo')) {
            preset = 'Lunes a Domingo';
        } else {
            preset = 'Personalizado';
            const days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
            custom = days.filter(d => str.toLowerCase().includes(d.toLowerCase()));
        }

        return { preset, start, end, custom };
    };

    // Effect to sync widget values to the main form field
    useEffect(() => {
        if (formData.rol === 'PSICOLOGO') {
            let diasText = '';
            if (diasPreset === 'Personalizado') {
                diasText = selectedDays.length > 0 ? selectedDays.join(', ') : 'Sin días';
            } else {
                diasText = diasPreset;
            }
            const fullHorario = `${diasText} ${horaInicio} - ${horaFin}`;
            setFormData(prev => ({ ...prev, horario_atencion: fullHorario }));
        }
    }, [diasPreset, selectedDays, horaInicio, horaFin, formData.rol]);

    useEffect(() => {
        fetchPsicologos();
    }, []);

    const fetchPsicologos = async () => {
        try {
            setLoading(true);
            const response = await apiClient.get('usuarios/');
            setPsicologos(response.data);
            setError('');
        } catch (err) {
            setError('Error al cargar la lista de personal.');
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmmit = async (e) => {
        e.preventDefault();
        
        try {
            if (formData.id) {
                // UPDATE (PUT/PATCH no está implementado full en UserSerializer con contraseñas de forma simple, 
                const payload = { ...formData };
                if (!payload.password) delete payload.password;
                if (payload.rol !== 'PSICOLOGO') {
                    payload.especialidad = null;
                    payload.horario_atencion = null;
                }

                await apiClient.put(`usuarios/${formData.id}/`, payload);
                alert("Psicólogo actualizado correctamente.");
            } else {
                // CREATE
                await apiClient.post('usuarios/', formData);
                alert("Psicólogo creado correctamente.");
            }
            setShowModal(false);
            fetchPsicologos();
        } catch (err) {
            const errorData = err.response?.data;
            const errorStr = typeof errorData === 'string'
                ? errorData
                : (Array.isArray(errorData) ? errorData[0] : (errorData?.detail || JSON.stringify(errorData || err.message)));

            if (errorStr && (errorStr.includes("Límite excedido") || errorStr.includes("limite") || errorStr.includes("excedido"))) {
                setLimitMessage(errorStr);
                setShowLimitModal(true);
            } else {
                alert("Error al guardar: " + errorStr);
            }
        }
    };

    const openCreateModal = () => {
        setDiasPreset('Lunes a Viernes');
        setSelectedDays([]);
        setHoraInicio('08:00');
        setHoraFin('16:00');
        setFormData({ id: null, username: '', email: '', password: '', rol: 'PSICOLOGO', especialidad: '', horario_atencion: 'Lunes a Viernes 08:00 - 16:00' });
        setShowModal(true);
    };

    const openEditModal = (p) => {
        const parsed = parseHorario(p.horario_atencion);
        setDiasPreset(parsed.preset);
        setSelectedDays(parsed.custom);
        setHoraInicio(parsed.start);
        setHoraFin(parsed.end);

        setFormData({
            id: p.id,
            username: p.username,
            email: p.email,
            password: '', // No traer la contraseña
            rol: p.rol || 'PSICOLOGO',
            especialidad: p.especialidad || '',
            horario_atencion: p.horario_atencion || '',
        });
        setShowModal(true);
    };

    const handleDelete = async (id) => {
        if (!window.confirm("¿Está seguro de eliminar a este psicólogo? Esta acción no se puede deshacer.")) return;
        
        try {
            await apiClient.delete(`usuarios/${id}/`);
            alert("Psicólogo eliminado.");
            fetchPsicologos();
        } catch (err) {
            alert("Error al eliminar al profesional.");
        }
    };

    return (
        <div style={styles.container}>
            {/* Header del Dashboard/Página */}
            <header style={styles.header}>
                <div>
                    <h1 style={styles.headerTitle}>Gestión de Personal Clínico</h1>
                    <p style={styles.headerSubtitle}>Administración de Psicólogos - Nivel Tenant</p>
                </div>
                <div>
                    <button style={styles.btnSecondary} onClick={() => navigate('/dashboard')}>
                        Volver al Dashboard
                    </button>
                    <button style={styles.btnPrimary} onClick={openCreateModal}>
                        + Registrar Personal
                    </button>
                </div>
            </header>

            {error && <div style={styles.errorBox}>{error}</div>}

            {/* Tabla de Psicólogos */}
            <div style={styles.card}>
                {loading ? (
                    <p>Cargando personal...</p>
                ) : psicologos.length === 0 ? (
                    <p style={{ color: '#64748b' }}>No hay psicólogos registrados en la clínica.</p>
                ) : (
                    <table style={styles.table}>
                        <thead>
                            <tr>
                                <th style={styles.th}>ID</th>
                                <th style={styles.th}>Personal / Usuario</th>
                                <th style={styles.th}>Correo</th>
                                <th style={styles.th}>Rol</th>
                                <th style={styles.th}>Especialidad</th>
                                <th style={styles.th}>Horarios</th>
                                <th style={styles.th}>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {psicologos.map(p => (
                                <tr key={p.id} style={styles.tr}>
                                    <td style={styles.td}>#{p.id}</td>
                                    <td style={{ ...styles.td, fontWeight: 'bold' }}>{p.username}</td>
                                    <td style={styles.td}>{p.email}</td>
                                    <td style={styles.td}>
                                        <span style={{...styles.badge, backgroundColor: p.rol === 'ADMIN' ? '#fee2e2' : p.rol === 'RECEPCIONISTA' ? '#f3e8ff' : '#dbeafe', color: p.rol === 'ADMIN' ? '#991b1b' : p.rol === 'RECEPCIONISTA' ? '#6b21a8' : '#1d4ed8'}}>
                                            {p.rol}
                                        </span>
                                    </td>
                                    <td style={styles.td}>
                                        {p.rol === 'PSICOLOGO' ? <span style={styles.badge}>{p.especialidad || 'General'}</span> : '-'}
                                    </td>
                                    <td style={styles.td}>{p.rol === 'PSICOLOGO' ? (p.horario_atencion || 'No definido') : '-'}</td>
                                    <td style={styles.td}>
                                        <button style={styles.btnEdit} onClick={() => openEditModal(p)}>Editar</button>
                                        <button style={styles.btnDelete} onClick={() => handleDelete(p.id)}>Eliminar</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            {/* Modal Formulario */}
            {showModal && (
                <div style={styles.modalOverlay}>
                    <div style={styles.modalContent}>
                        <h2 style={{marginTop: 0}}>{formData.id ? 'Editar Personal / Usuario' : 'Registro de Personal / Usuario'}</h2>
                        {/* [ALINEACIÓN RF-28/RF-04] - Formulario dinámico: Restricción de campos clínicos para roles administrativos y obligatoriedad para operativos. */}
                        <form onSubmit={handleSubmmit}>
                            <div style={styles.inputGroup}>
                                <label style={styles.label}>Nombre de Usuario</label>
                                <input required type="text" name="username" value={formData.username} onChange={handleInputChange} style={styles.input} />
                            </div>
                            <div style={styles.inputGroup}>
                                <label style={styles.label}>Correo Electrónico</label>
                                <input required type="email" name="email" value={formData.email} onChange={handleInputChange} style={styles.input} />
                            </div>
                            <div style={styles.inputGroup}>
                                <label style={styles.label}>{formData.id ? 'Nueva Contraseña (Opcional)' : 'Contraseña'}</label>
                                <input required={!formData.id} type="password" name="password" value={formData.password} onChange={handleInputChange} style={styles.input} />
                            </div>
                            {!formData.id && (
                                <div style={styles.inputGroup}>
                                    <label style={styles.label}>Confirmar Contraseña</label>
                                    <input required type="password" name="password_confirm" value={formData.password_confirm} onChange={handleInputChange} style={styles.input} />
                                </div>
                            )}
                            <div style={styles.inputGroup}>
                                <label style={styles.label}>Rol en la Clínica</label>
                                <select required name="rol" value={formData.rol} onChange={handleInputChange} style={styles.input}>
                                    <option value="PSICOLOGO">Psicólogo</option>
                                    <option value="ADMIN">Administrador</option>
                                </select>
                            </div>

                            {formData.rol === 'PSICOLOGO' && (
                                <>
                                    <div style={styles.inputGroup}>
                                        <label style={styles.label}>Especialidad (RF-04)</label>
                                        <input required type="text" name="especialidad" placeholder="Ej. Psicología Clínica..." value={formData.especialidad} onChange={handleInputChange} style={styles.input} />
                                    </div>
                                    <div style={styles.inputGroup}>
                                        <label style={styles.label}>Horario de Atención (RF-04)</label>
                                        
                                        {/* Rango de Días Preset */}
                                        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '10px' }}>
                                            {['Lunes a Viernes', 'Lunes a Sábado', 'Lunes a Domingo', 'Personalizado'].map(preset => (
                                                <button
                                                    key={preset}
                                                    type="button"
                                                    style={{
                                                        ...styles.btnCapsule,
                                                        ...(diasPreset === preset ? styles.btnCapsuleActive : {})
                                                    }}
                                                    onClick={() => setDiasPreset(preset)}
                                                >
                                                    {preset}
                                                </button>
                                            ))}
                                        </div>

                                        {/* Días específicos (si es Personalizado) */}
                                        {diasPreset === 'Personalizado' && (
                                            <div style={{ display: 'flex', gap: '6px', justifyContent: 'center', marginBottom: '15px' }}>
                                                {['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'].map(day => {
                                                    const isSelected = selectedDays.includes(day);
                                                    return (
                                                        <button
                                                            key={day}
                                                            type="button"
                                                            title={day}
                                                            style={{
                                                                ...styles.dayCircle,
                                                                ...(isSelected ? styles.dayCircleActive : {})
                                                            }}
                                                            onClick={() => {
                                                                if (isSelected) {
                                                                    setSelectedDays(selectedDays.filter(d => d !== day));
                                                                } else {
                                                                    setSelectedDays([...selectedDays, day]);
                                                                }
                                                            }}
                                                        >
                                                            {day[0]}
                                                        </button>
                                                    );
                                                })}
                                            </div>
                                        )}

                                        {/* Selector de Horas */}
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px' }}>
                                            <div style={{ flex: 1 }}>
                                                <label style={{ ...styles.label, fontSize: '11px', marginBottom: '2px' }}>Desde</label>
                                                <select
                                                    value={horaInicio}
                                                    onChange={e => setHoraInicio(e.target.value)}
                                                    style={styles.input}
                                                >
                                                    {['07:00', '07:30', '08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30', '22:00'].map(h => (
                                                        <option key={h} value={h}>{h}</option>
                                                    ))}
                                                </select>
                                            </div>
                                            <div style={{ flex: 1 }}>
                                                <label style={{ ...styles.label, fontSize: '11px', marginBottom: '2px' }}>Hasta</label>
                                                <select
                                                    value={horaFin}
                                                    onChange={e => setHoraFin(e.target.value)}
                                                    style={styles.input}
                                                >
                                                    {['07:00', '07:30', '08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30', '22:00'].map(h => (
                                                        <option key={h} value={h}>{h}</option>
                                                    ))}
                                                </select>
                                            </div>
                                        </div>

                                        {/* Vista previa del formato */}
                                        <div style={{ fontSize: '12px', color: '#1e293b', backgroundColor: '#f1f5f9', padding: '10px', borderRadius: '8px', borderLeft: '4px solid #2563eb', fontWeight: 'bold' }}>
                                            🕒 Vista previa: {formData.horario_atencion || 'No definido'}
                                        </div>
                                    </div>
                                </>
                            )}
                            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '20px' }}>
                                <button type="button" style={styles.btnSecondary} onClick={() => setShowModal(false)}>Cancelar</button>
                                <button type="submit" style={styles.btnPrimary}>{formData.id ? 'Actualizar Usuario' : 'Crear Usuario'}</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Modal de Límite de Suscripción Excedido (Incentivo de Venta SaaS) */}
            {showLimitModal && (
                <div style={styles.limitModalOverlay}>
                    <div style={styles.limitModalContent}>
                        <div style={styles.limitIconContainer}>
                            <span style={{ fontSize: '48px' }}>👑</span>
                        </div>
                        <h3 style={styles.limitModalTitle}>¡Límite de Plan Alcanzado!</h3>
                        <p style={styles.limitModalText}>{limitMessage}</p>
                        <div style={styles.limitIncentiveCard}>
                            <p style={{ margin: 0, fontWeight: 'bold', color: '#1e293b' }}>
                                ¡Haz crecer tu clínica hoy!
                            </p>
                            <p style={{ margin: '4px 0 0 0', color: '#64748b' }}>
                                Actualiza a un plan superior para registrar pacientes y psicólogos sin restricciones.
                            </p>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '25px', width: '100%' }}>
                            <button 
                                onClick={() => {
                                    setShowLimitModal(false);
                                    setShowModal(false);
                                    navigate('/suscripcion');
                                }}
                                style={styles.limitBtnUpgrade}
                            >
                                🚀 ACTUALIZAR PLAN AHORA
                            </button>
                            <button 
                                onClick={() => setShowLimitModal(false)}
                                style={styles.limitBtnCancel}
                            >
                                Mantener plan actual
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

// ===============================================
// ESTILOS
// ===============================================
const styles = {
    container: {
        padding: '30px',
        maxWidth: '1200px',
        margin: '0 auto',
        backgroundColor: '#f8fafc',
        minHeight: '100vh',
    },
    header: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '30px',
    },
    headerTitle: { margin: 0, fontSize: '24px', color: '#0f172a' },
    headerSubtitle: { margin: 0, fontSize: '14px', color: '#64748b' },
    card: {
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '24px',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        overflowX: 'auto',
    },
    table: { width: '100%', borderCollapse: 'collapse', textAlign: 'left' },
    th: {
        padding: '12px 16px', borderBottom: '2px solid #e2e8f0',
        color: '#475569', fontWeight: 'bold', fontSize: '14px'
    },
    tr: { borderBottom: '1px solid #e2e8f0' },
    td: { padding: '16px', color: '#1e293b', fontSize: '14px' },
    badge: {
        backgroundColor: '#dbeafe', color: '#1d4ed8', padding: '4px 8px', borderRadius: '12px', fontSize: '12px', fontWeight: 'bold'
    },
    btnPrimary: {
        backgroundColor: '#2563eb', color: 'white', padding: '10px 16px', border: 'none', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', marginLeft: '10px'
    },
    btnSecondary: {
        backgroundColor: '#fff', color: '#475569', padding: '10px 16px', border: '1px solid #cbd5e1', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold'
    },
    btnEdit: { backgroundColor: '#f59e0b', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', marginRight: '8px', fontSize: '12px', fontWeight: 'bold' },
    btnDelete: { backgroundColor: '#ef4444', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px', fontWeight: 'bold' },
    errorBox: { padding: '12px', backgroundColor: '#fef2f2', color: '#b91c1c', border: '1px solid #fecaca', borderRadius: '8px', marginBottom: '20px' },
    // Modal
    modalOverlay: {
        position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000
    },
    modalContent: {
        backgroundColor: 'white', 
        padding: '30px', 
        borderRadius: '12px', 
        width: '100%', 
        maxWidth: '400px',
        maxHeight: '90vh',
        overflowY: 'auto',
    },
    inputGroup: { marginBottom: '15px' },
    label: { display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold', color: '#475569' },
    input: { width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1', boxSizing: 'border-box' },
    btnCapsule: {
        padding: '6px 12px',
        borderRadius: '20px',
        border: '1px solid #cbd5e1',
        backgroundColor: '#fff',
        color: '#475569',
        fontSize: '11px',
        fontWeight: 'bold',
        cursor: 'pointer',
        transition: 'all 0.2s',
    },
    btnCapsuleActive: {
        backgroundColor: '#2563eb',
        color: '#fff',
        borderColor: '#2563eb',
    },
    dayCircle: {
        width: '32px',
        height: '32px',
        borderRadius: '50%',
        border: '1px solid #cbd5e1',
        backgroundColor: '#fff',
        color: '#475569',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '11px',
        fontWeight: 'bold',
        cursor: 'pointer',
        transition: 'all 0.2s',
    },
    dayCircleActive: {
        backgroundColor: '#2563eb',
        color: '#fff',
        borderColor: '#2563eb',
    },
    limitModalOverlay: {
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        backgroundColor: 'rgba(15, 23, 42, 0.65)',
        backdropFilter: 'blur(8px)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 2000
    },
    limitModalContent: {
        backgroundColor: 'white',
        padding: '35px',
        borderRadius: '20px',
        width: '100%',
        maxWidth: '420px',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
        border: '1px solid #e2e8f0'
    },
    limitIconContainer: {
        width: '80px',
        height: '80px',
        borderRadius: '50%',
        backgroundColor: '#fef3c7',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: '20px'
    },
    limitModalTitle: {
        margin: '0 0 10px 0',
        fontSize: '20px',
        fontWeight: '900',
        color: '#0f172a'
    },
    limitModalText: {
        fontSize: '13.5px',
        color: '#ef4444',
        margin: '0 0 20px 0',
        fontWeight: '600',
        lineHeight: '1.5',
        backgroundColor: '#fef2f2',
        padding: '10px 15px',
        borderRadius: '8px',
        border: '1px solid #fecaca'
    },
    limitIncentiveCard: {
        backgroundColor: '#f8fafc',
        padding: '15px',
        borderRadius: '10px',
        border: '1px solid #cbd5e1',
        fontSize: '12px',
        lineHeight: '1.5'
    },
    limitBtnUpgrade: {
        width: '100%',
        padding: '14px',
        backgroundColor: '#2563eb',
        color: 'white',
        border: 'none',
        borderRadius: '8px',
        fontWeight: 'bold',
        cursor: 'pointer',
        fontSize: '13px',
        boxShadow: '0 4px 6px -1px rgba(37, 99, 235, 0.2)'
    },
    limitBtnCancel: {
        width: '100%',
        padding: '12px',
        backgroundColor: 'transparent',
        color: '#64748b',
        border: 'none',
        borderRadius: '8px',
        fontWeight: '600',
        cursor: 'pointer',
        fontSize: '12px'
    }
};

export default GestionPersonal;
