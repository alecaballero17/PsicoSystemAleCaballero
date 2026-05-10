// ==============================================================================
// [SPRINT 2 - T026] Service Layer: API Client para Historia Clínica e IA
// [IA-01] Análisis predictivo con Gemini
// ==============================================================================
import apiClient from '../api/axiosConfig';

const historiaService = {
    /**
     * T026: Obtener historias clínicas del tenant.
     */
    getHistorias: async () => {
        const response = await apiClient.get('historias/');
        return response.data;
    },

    /**
     * T026: Obtener historia clínica específica.
     */
    getHistoria: async (id) => {
        const response = await apiClient.get(`historias/${id}/`);
        return response.data;
    },

    /**
     * T026: Obtener evoluciones (notas de sesión).
     */
    getEvoluciones: async () => {
        const response = await apiClient.get('evoluciones/');
        return response.data;
    },

    /**
     * T026: Crear nota de evolución con soporte multipart para archivos adjuntos.
     */
    crearEvolucion: async (data, archivoAdjunto = null) => {
        if (archivoAdjunto) {
            const formData = new FormData();
            formData.append('historia', data.historia);
            formData.append('notas_sesion', data.notas_sesion);
            formData.append('archivo_adjunto', archivoAdjunto);

            const response = await apiClient.post('evoluciones/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            return response.data;
        }

        const response = await apiClient.post('evoluciones/', data);
        return response.data;
    },

    /**
     * IA-01: Ejecutar análisis predictivo de IA sobre una evolución.
     */
    analizarConIA: async (evolucionId) => {
        const response = await apiClient.post(`ia/analizar/${evolucionId}/`);
        return response.data;
    },
};

export default historiaService;
