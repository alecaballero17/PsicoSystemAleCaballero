import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/axiosConfig';

const RegistroCita = () => {
    const navigate = useNavigate();
    const [pacientes, setPacientes] = useState([]);
    const [psicologos, setPsicologos] = useState([]);
    const [formData, setFormData] = useState({
        paciente: '',
        psicologo: '',
        fecha_hora: '',
        motivo: '',
        duracion_minutos: 60
    });
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [resPac, resPsi] = await Promise.all([
                    apiClient.get('pacientes/'),
                    apiClient.get('psicologos/') 
                ]);
                setPacientes(resPac.data);
                setPsicologos(resPsi.data || []); 
            } catch (err) {
                console.error("Error cargando datos", err);
            }
        };
        fetchData();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await apiClient.post('logistica/gestion/', formData);
            alert("¡Cita programada con éxito!");
            navigate('/citas');
        } catch (err) {
            const errorMsg = err.response?.data?.non_field_errors?.[0] || err.response?.data?.[0] || "Error al programar la cita. Verifique traslapes de horario.";
            alert(errorMsg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.container}>
            <div style={styles.card}>
                <button onClick={() => navigate('/citas')} style={styles.btnBack}>← Volver</button>
                <h2 style={styles.title}>Programar Nueva Cita (T032)</h2>
                
                <form onSubmit={handleSubmit}>
                    <div style={styles.group}>
                        <label>Paciente:</label>
                        <select 
                            required 
                            style={styles.input}
                            value={formData.paciente}
                            onChange={(e) => setFormData({...formData, paciente: e.target.value})}
                        >
                            <option value="">Seleccione un paciente...</option>
                            {pacientes.map(p => <option key={p.id} value={p.id}>{p.nombre}</option>)}
                        </select>
                    </div>

                    <div style={styles.group}>
                        <label>Psicólogo:</label>
                        <select 
                            required 
                            style={styles.input}
                            value={formData.psicologo}
                            onChange={(e) => setFormData({...formData, psicologo: e.target.value})}
                        >
                            <option value="">Seleccione profesional...</option>
                            {psicologos.map(p => <option key={p.id} value={p.id}>{p.name || p.username}</option>)}
                        </select>
                    </div>

                    <div style={styles.group}>
                        <label>Fecha y Hora:</label>
                        <input 
                            type="datetime-local" 
                            required 
                            style={styles.input}
                            value={formData.fecha_hora}
                            onChange={(e) => setFormData({...formData, fecha_hora: e.target.value})}
                        />
                    </div>

                    <div style={styles.group}>
                        <label>Motivo de Consulta:</label>
                        <textarea 
                            style={styles.input}
                            rows="3"
                            value={formData.motivo}
                            onChange={(e) => setFormData({...formData, motivo: e.target.value})}
                        ></textarea>
                    </div>

                    <button type="submit" disabled={loading} style={styles.btnSubmit}>
                        {loading ? 'Guardando...' : 'Confirmar Cita'}
                    </button>
                </form>
            </div>
        </div>
    );
};

const styles = {
    container: { display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', backgroundColor: '#f1f5f9', padding: '20px' },
    card: { backgroundColor: 'white', padding: '40px', borderRadius: '16px', boxShadow: '0 10px 25px rgba(0,0,0,0.1)', width: '100%', maxWidth: '500px' },
    btnBack: { border: 'none', background: 'none', color: '#64748b', cursor: 'pointer', marginBottom: '20px' },
    title: { fontSize: '24px', color: '#1e293b', marginBottom: '30px', fontWeight: 'bold' },
    group: { marginBottom: '20px' },
    input: { width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid #cbd5e1', marginTop: '5px' },
    btnSubmit: { width: '100%', padding: '14px', backgroundColor: '#2563eb', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', marginTop: '10px' }
};

export default RegistroCita;
