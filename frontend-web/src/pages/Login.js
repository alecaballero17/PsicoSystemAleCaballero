// [CIERRE SPRINT 1] Flujo SaaS integrado: Login aislado.
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import { loginStyles as styles } from '../styles/loginStyles'; 
import { useAuth } from '../context/AuthContext'; // 1. IMPORTAMOS EL MEGÁFONO

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    
    const navigate = useNavigate();
    const { login, user } = useAuth(); // 2. SACAMOS LA FUNCIÓN PARA TRANSMITIR

    // Redirección si ya está autenticado (RBAC T018)
    useEffect(() => {
        if (user) {
            navigate('/dashboard');
        }
    }, [user, navigate]);

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            // 3. El servicio hace el trabajo sucio (habla con Django y guarda en localStorage)
            await authService.login(username, password);
            
            // 4. ¡ANUNCIAMOS A LA RADIO! (Actualizamos la RAM)
            // Leemos rápido del cajón lo que el authService acaba de guardar
            login({
                token: localStorage.getItem('userToken'),
                role: localStorage.getItem('userRole'),
                name: localStorage.getItem('userName'),
                clinica_id: localStorage.getItem('clinica_id')
            });

            // 5. Redirigimos al sistema
            navigate('/dashboard');
        } catch (error) {
            alert("Credenciales incorrectas. Verifique su acceso.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.container}>
            <div style={styles.card}>
                <div style={styles.logoIcon}>⚕️</div>
                <h1 style={styles.title}>PsicoSystem</h1>
                <p style={styles.subtitle}>Gestión Clínica Universitaria</p>
                
                <form onSubmit={handleLogin}>
                    <div style={styles.inputGroup}>
                        <label style={styles.label}>Usuario</label>
                        <input 
                            type="text" 
                            style={styles.input}
                            value={username}
                            onChange={e => setUsername(e.target.value)} 
                            required 
                        />
                    </div>
                    <div style={styles.inputGroup}>
                        <label style={styles.label}>Contraseña</label>
                        <input 
                            type="password" 
                            style={styles.input}
                            value={password}
                            autoComplete="current-password"
                            onChange={e => setPassword(e.target.value)} 
                            required 
                        />
                    </div>
                    <button 
                        type="submit" 
                        disabled={loading} 
                        style={{
                            ...styles.button, 
                            backgroundColor: loading ? '#94a3b8' : '#2563eb'
                        }}
                    >
                        {loading ? 'Verificando...' : 'Entrar al Sistema'}
                    </button>
                    {/* [SPRINT 1 - T019] [CU-03] Enlace al flujo de recuperación de credenciales */}
                    <div style={{ textAlign: 'center', marginTop: '16px' }}>
                        <button
                            type="button"
                            onClick={() => navigate('/recuperar')}
                            style={{ background: 'none', border: 'none', color: '#2563eb', fontSize: '13px', cursor: 'pointer', textDecoration: 'underline' }}
                        >
                            ¿Olvidaste tu contraseña?
                        </button>
                    </div>

                    <div style={{ textAlign: 'center', marginTop: '16px', borderTop: '1px solid #e2e8f0', paddingTop: '16px' }}>
                        <button
                            type="button"
                            onClick={() => navigate('/')}
                            style={{ background: 'none', border: 'none', color: '#475569', fontSize: '13px', cursor: 'pointer', fontWeight: '600' }}
                        >
                            ← Volver al Portal Principal
                        </button>
                    </div>
                </form>
                <p style={styles.footerText}>UAGRM - Sistemas II</p>
            </div>
        </div>
    );
};

export default Login;