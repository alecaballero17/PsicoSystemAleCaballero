import apiClient from '../api/axiosConfig';

const dashboardService = {
    /**
     * T008: Consumo de métricas calculadas en servidor para optimizar el cliente (RNF-01).
     * Obtiene el conteo de pacientes, citas y estado del sistema.
     */
    getMetrics: async () => {
        try {
            // LLAMADA LIMPIA: apiClient ya sabe a qué IP apuntar y pone el Token automáticamente
            const response = await apiClient.get('dashboard/');
            return response.data;
            
        } catch (error) {
            console.error("Error en dashboardService:", error);
            
            // Graceful Degradation: Si falla, devolvemos 0s para que la pantalla no se quede en blanco
            return {
                total_pacientes: 0,
                citas_hoy: 0,
                error: true
            };
        }
    }
};

export default dashboardService;