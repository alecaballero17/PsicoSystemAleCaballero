// [SPRINT 0 - T008] Conectividad Base: Configuración del cliente HTTP centralizado.
// [SPRINT 0 - T002] Stack Tecnológico: Axios como librería HTTP para React.
// [RNF-03] Seguridad: Inyección automática de JWT en cada petición.
// [RNF-05] Compatibilidad: Base URL configurable por entorno.
import axios from 'axios';

// [SPRINT 0 - T008] Extraemos la IP del .env o usamos localhost por defecto
const API_BASE = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/api';

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

// INTERCEPTOR DE RESPUESTA: Maneja errores 401 (Token expirado) globalmente
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.clear();
            window.location.href = '/';
        }
        return Promise.reject(error);
    }
);

export default apiClient;