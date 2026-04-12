import apiClient from '../api/axiosConfig'; // <-- IMPORTAMOS EL CLIENTE CENTRALIZADO

const login = async (username, password) => {
    try {
        // T011: Petición POST usando la base URL de apiClient
        const response = await apiClient.post('auth/login/', {
            username: username,
            password: password,
        });

        // Si la respuesta es exitosa (200 OK), gestionamos la persistencia física
        if (response.data.access) {
            // Guardamos los tokens para mantener la sesión activa (RNF-03)
            localStorage.setItem('userToken', response.data.access);
            localStorage.setItem('refreshToken', response.data.refresh);
            
            // MEJORA: Guardamos el perfil para evitar peticiones redundantes
            localStorage.setItem('userName', username.toUpperCase());
            
            // Asignamos el rol (RF-28)
            const role = response.data.role || 'ADMIN'; 
            localStorage.setItem('userRole', role);

            // [ALINEACIÓN SPRINT 1 - RF-29] Bypass Global: Persistir Tenant ID localmente
            if (response.data.clinica_id) {
                localStorage.setItem('clinica_id', response.data.clinica_id);
            } else {
                localStorage.removeItem('clinica_id');
            }
        }

        return response.data;
    } catch (error) {
        throw error;
    }
};

/**
 * CU-04: Finalización de Sesión
 * Limpia el storage físico y el Blacklist de Tokens
 */
const logout = async () => {
    const refreshToken = localStorage.getItem('refreshToken');
    if (refreshToken) {
        try {
            // Nota de Arquitectura: Ya no pasamos headers manuales. 
            // apiClient inyecta el 'Bearer token' automáticamente.
            await apiClient.post('auth/logout/', { refresh: refreshToken });
        } catch (error) {
            console.error("Error en logout API:", error);
        }
    }
    
    // Limpieza de rastros físicos
    localStorage.removeItem('userToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('userName');
    localStorage.removeItem('userRole');
    localStorage.removeItem('clinica_id');
};

// =========================================================
// ---> AQUÍ ESTÁ LO QUE FALTABA (La adopción del huérfano)
// =========================================================
const getCurrentUser = async () => {
    try {
        // T009: Validación de sesión persistente (Anti-huérfano)
        // Llama al endpoint /api/auth/me/ para verificar que el token es válido
        const response = await apiClient.get('auth/me/');
        return response.data; 
    } catch (error) {
        return null; // Si el token expiró o es inválido, devuelve null
    }
};

const authService = {
    login,
    logout,
    getCurrentUser,
    apiClient // <-- Exportamos el cliente para peticiones contextuales
};

export default authService;