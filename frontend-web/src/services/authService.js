import axios from 'axios';

// T011: Configuración de la URL base alineada con el Backend Django
const API_URL = 'http://127.0.0.1:8000/api/auth/';

const login = async (username, password) => {
    try {
        // Petición POST enviando las credenciales al endpoint de SimpleJWT
        const response = await axios.post(`${API_URL}login/`, {
            username: username,
            password: password,
        });

        // Si la respuesta es exitosa (200 OK), gestionamos la persistencia de sesión
        if (response.data.access) {
            // Guardamos los tokens para mantener la sesión activa (RNF-03)
            localStorage.setItem('userToken', response.data.access);
            localStorage.setItem('refreshToken', response.data.refresh);
            
            /** * MEJORA PARA EL DASHBOARD:
             * Guardamos los datos de perfil que el backend devuelve en el login 
             * para evitar peticiones redundantes en el primer render.
             */
            localStorage.setItem('userName', username.toUpperCase());
            
            // Asignamos un rol por defecto si el backend no lo envía aún (para el Sprint 1)
            // Esto permite que el Dashboard active el modo "ADMIN" o "PSICOLOGO" (RF-28)
            const role = response.data.role || 'ADMIN'; 
            localStorage.setItem('userRole', role);
        }

        return response.data;
    } catch (error) {
        // Lanzamos el error para que el componente Login lo capture y muestre el alert
        throw error;
    }
};

/**
 * CU-04: Finalización de Sesión
 * Esta función limpia el storage y prepara el sistema para el S2-04 (Blacklist de Tokens)
 */
const logout = async () => {
    const refreshToken = localStorage.getItem('refreshToken');
    if (refreshToken) {
        try {
            await axios.post(`${API_URL}logout/`, { refresh: refreshToken }, {
                headers: { Authorization: `Bearer ${localStorage.getItem('userToken')}` }
            });
        } catch (error) {
            console.error("Error en logout API:", error);
        }
    }
    localStorage.removeItem('userToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('userName');
    localStorage.removeItem('userRole');
    localStorage.removeItem('clinica_id');
};

const authService = {
    login,
    logout
};

export default authService;