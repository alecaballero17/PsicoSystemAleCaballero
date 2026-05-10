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
            alert("Error al guardar: " + JSON.stringify(err.response?.data || err.message));
        }
    };

    const openCreateModal = () => {
        setFormData({ id: null, username: '', email: '', password: '', password_confirm: '', rol: 'PSICOLOGO', especialidad: '', horario_atencion: '' });
        setShowModal(true);
    };

    const openEditModal = (p) => {
        setFormData({
            id: p.id,
            username: p.username,
            email: p.email,
            password: '', // No traer la contraseña
            password_confirm: '',
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
                            <div style={styles.inputGroup}>
                                <label style={styles.label}>{formData.id ? 'Confirmar Nueva Contraseña' : 'Confirmar Contraseña'}</label>
                                <input required={!formData.id} type="password" name="password_confirm" value={formData.password_confirm} onChange={handleInputChange} style={styles.input} />
                            </div>
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
                                        <input required type="text" name="horario_atencion" placeholder="Ej. Lunes a Viernes 08:00 - 16:00" value={formData.horario_atencion} onChange={handleInputChange} style={styles.input} />
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
        backgroundColor: 'white', padding: '30px', borderRadius: '12px', width: '100%', maxWidth: '400px',
    },
    inputGroup: { marginBottom: '15px' },
    label: { display: 'block', marginBottom: '5px', fontSize: '13px', fontWeight: 'bold', color: '#475569' },
    input: { width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1', boxSizing: 'border-box' }
};

export default GestionPersonal;
