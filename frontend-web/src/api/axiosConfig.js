// [SPRINT 0 - T008] Conectividad Base: Configuración del cliente HTTP centralizado.
// [SPRINT 0 - T002] Stack Tecnológico: Axios como librería HTTP para React.
// [RNF-03] Seguridad: Inyección automática de JWT en cada petición.
// [RNF-05] Compatibilidad: Base URL configurable por entorno (.env).
import axios from 'axios';

// [SPRINT 0 - T008] Extraemos la IP del .env o usamos localhost por defecto
const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/api';
const API_BASE = API_URL.endsWith('/') ? API_URL : `${API_URL}/`;

const apiClient = axios.create({
    baseURL: API_BASE,
    headers: {
        'Content-Type': 'application/json',
    }
});

// INTERCEPTOR: Inyecta el token JWT automáticamente en cada petición
apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('userToken');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// [ALINEACIÓN SPRINT 1 - T011/T022] Interceptor de respuesta: Maneja tokens expirados
// Solo redirige en 401 de endpoints PROTEGIDOS; no interfiere con login/logout
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        const url = error.config?.url || '';
        const isAuthEndpoint = url.includes('auth/login') || url.includes('auth/logout') || url.includes('auth/password-reset');
        if (error.response?.status === 401 && !isAuthEndpoint) {
            localStorage.clear();
            window.location.href = '/';
        }
        return Promise.reject(error);
    }
);

export default apiClient;