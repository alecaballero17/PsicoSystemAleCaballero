import apiClient from '../api/axiosConfig';

const pacienteService = {
    // T014: Listar pacientes usando el cliente centralizado (Requerido para el Dashboard)
    getPacientes: async () => {
        const response = await apiClient.get('/pacientes/');
        return response.data;
    },

    // CU-02: Registrar paciente
    registrarPaciente: async (formData) => {
        // Nota de Arquitectura: Ya no verificamos el token ni los headers manualmente aquí.
        // El interceptor de apiClient (axiosConfig) se encarga de inyectar el JWT 
        // para el aislamiento Multi-tenant (RF-29).
        const response = await apiClient.post('/pacientes/registrar/', formData);
        return response.data;
    }
};

export default pacienteService;