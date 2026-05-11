import apiClient from '../api/axiosConfig';

const pacienteService = {
    // T014: Listar pacientes usando el cliente centralizado (Requerido para el Dashboard)
    getPacientes: async () => {
        const response = await apiClient.get('pacientes/');
        return response.data;
    },

    // CU-02: Registrar paciente
    registrarPaciente: async (formData) => {
        // Corregido: El endpoint correcto para crear es 'pacientes/' (POST)
        const response = await apiClient.post('pacientes/', formData);
        return response.data;
    }
};

export default pacienteService;