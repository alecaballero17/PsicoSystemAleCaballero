import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import pacienteService from '../services/pacienteService'; // Importamos la lógica
import { registroStyles as styles } from '../styles/registroStyles'; // Importamos los estilos

const RegistroPaciente = () => {
    const [formData, setFormData] = useState({ nombre: '', ci: '', fecha_nacimiento: '', telefono: '' });
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await pacienteService.registrarPaciente(formData);
            if ("Notification" in window) {
                if (Notification.permission === "granted") {
                    new Notification("PsicoSystem Clínico", { body: "¡Expediente de paciente creado con éxito!", icon: "/favicon.ico" });
                }
            }
            alert("¡Paciente guardado exitosamente!");
            navigate('/dashboard');
        } catch (error) {
            const msg = error.response?.data ? JSON.stringify(error.response.data) : "Error de conexión";
            alert("Error: " + msg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.pageBackground}>
            <div style={styles.card}>
                <button onClick={() => navigate('/dashboard')} style={styles.backButton}>
                    <span>←</span> Volver al panel
                </button>

                <h2 style={styles.title}>Nuevo Paciente</h2>
                <p style={styles.subtitle}>Expediente clínico (CU-02)</p>
                
                <form onSubmit={handleSubmit}>
                    {['Nombre Completo', 'Cédula de Identidad (CI)', 'Fecha de Nacimiento', 'Teléfono'].map((label, idx) => {
                        const fields = ['nombre', 'ci', 'fecha_nacimiento', 'telefono'];
                        const types = ['text', 'text', 'date', 'tel'];
                        return (
                            <div key={fields[idx]} style={styles.inputGroup}>
                                <label style={styles.label}>{label}</label>
                                <input 
                                    type={types[idx]}
                                    style={styles.input}
                                    onChange={e => setFormData({...formData, [fields[idx]]: e.target.value})} 
                                    required 
                                />
                            </div>
                        );
                    })}
                    <button type="submit" style={styles.submitButton} disabled={loading}>
                        {loading ? 'Guardando...' : 'Registrar Paciente'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default RegistroPaciente;