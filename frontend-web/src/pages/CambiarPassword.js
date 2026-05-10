import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/axiosConfig';

const CambiarPassword = () => {
    const navigate = useNavigate();
    const [passwords, setPasswords] = useState({
        new_password: '',
        confirm_password: ''
    });
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState({ text: '', type: '' });

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (passwords.new_password !== passwords.confirm_password) {
            setMessage({ text: 'Las contraseñas no coinciden.', type: 'error' });
            return;
        }

        try {
            setLoading(true);
            await apiClient.put('auth/change_password/', { new_password: passwords.new_password });
            setMessage({ text: 'Contraseña actualizada correctamente.', type: 'success' });
            setTimeout(() => navigate('/dashboard'), 2000);
        } catch (err) {
            setMessage({ text: 'Error al cambiar la contraseña. Mínimo 8 caracteres.', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.container}>
            <div style={styles.card}>
                <h2 style={styles.title}>🔐 Cambiar Contraseña</h2>
                <p style={styles.subtitle}>Asegura tu cuenta con una nueva clave</p>

                {message.text && (
                    <div style={{...styles.message, backgroundColor: message.type === 'success' ? '#dcfce7' : '#fef2f2', color: message.type === 'success' ? '#166534' : '#dc2626'}}>
                        {message.text}
                    </div>
                )}

                <form onSubmit={handleSubmit} style={styles.form}>
                    <div style={styles.field}>
                        <label style={styles.label}>Nueva Contraseña</label>
                        <input 
                            type="password" 
                            required 
                            minLength={8}
                            style={styles.input}
                            value={passwords.new_password}
                            onChange={(e) => setPasswords({...passwords, new_password: e.target.value})}
                        />
                    </div>
                    <div style={styles.field}>
                        <label style={styles.label}>Confirmar Contraseña</label>
                        <input 
                            type="password" 
                            required 
                            style={styles.input}
                            value={passwords.confirm_password}
                            onChange={(e) => setPasswords({...passwords, confirm_password: e.target.value})}
                        />
                    </div>
                    <button type="submit" disabled={loading} style={styles.btnSubmit}>
                        {loading ? 'ACTUALIZANDO...' : 'ACTUALIZAR CONTRASEÑA'}
                    </button>
                </form>
            </div>
        </div>
    );
};

const styles = {
    container: { display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 'calc(100vh - 100px)', padding: '20px' },
    card: { backgroundColor: 'white', padding: '40px', borderRadius: '20px', boxShadow: '0 10px 25px rgba(0,0,0,0.1)', width: '100%', maxWidth: '400px' },
    title: { margin: '0 0 10px 0', fontSize: '24px', textAlign: 'center', color: '#1e293b' },
    subtitle: { margin: '0 0 30px 0', textAlign: 'center', color: '#64748b', fontSize: '14px' },
    form: { display: 'flex', flexDirection: 'column', gap: '20px' },
    field: { display: 'flex', flexDirection: 'column', gap: '8px' },
    label: { fontSize: '13px', fontWeight: 'bold', color: '#475569' },
    input: { padding: '12px', borderRadius: '10px', border: '1px solid #e2e8f0', outline: 'none', transition: 'border 0.2s' },
    btnSubmit: { backgroundColor: '#2563eb', color: 'white', border: 'none', padding: '14px', borderRadius: '10px', fontWeight: 'bold', cursor: 'pointer', transition: 'background 0.2s' },
    message: { padding: '12px', borderRadius: '8px', marginBottom: '20px', textAlign: 'center', fontSize: '13px', fontWeight: '500' }
};

export default CambiarPassword;
