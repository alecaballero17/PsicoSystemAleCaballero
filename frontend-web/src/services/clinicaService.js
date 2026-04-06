// Mantenemos TU ruta correcta que apunta a la carpeta api/
import apiClient from '../api/axiosConfig';

const clinicaService = {
    // RF-29: Registrar una nueva Clínica (Tenant)
    registrarClinica: async (clinicaData) => {
        try {
            // apiClient inyecta automáticamente el token JWT
            const response = await apiClient.post('/clinicas/', clinicaData);
            return response.data;
        } catch (error) {
            // Capturamos el error en la capa de servicio antes de mandarlo a la UI
            console.error("Fallo en la capa de servicio (RF-29):", error);
            throw error; 
        }
    }
};

export default clinicaService;