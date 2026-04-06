import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import { loginStyles as styles } from '../styles/loginStyles'; 
import { useAuth } from '../context/AuthContext'; // 1. IMPORTAMOS EL MEGÁFONO

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    
    const navigate = useNavigate();
    const { login } = useAuth(); // 2. SACAMOS LA FUNCIÓN PARA TRANSMITIR

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
                name: localStorage.getItem('userName')
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
                </form>
                <p style={styles.footerText}>UAGRM - Sistemas II</p>
            </div>
        </div>
    );
};

export default Login;