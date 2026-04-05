import axios from 'axios';

// URL base apuntando a tu backend de Django
const API_URL = 'http://127.0.0.1:8000/api/dashboard/';

const dashboardService = {
    /**
     * T008: Consumo de métricas calculadas en servidor para optimizar el cliente (RNF-01).
     * Obtiene el conteo de pacientes, citas y estado del sistema.
     */
    getMetrics: async () => {
        const token = localStorage.getItem('userToken');
        
        try {
            const response = await axios.get(API_URL, {
                headers: { 
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            // Retornamos los datos (total_pacientes, citas_hoy, etc.)
            return response.data;
            
        } catch (error) {
            console.error("Error en dashboardService:", error.response?.data || error.message);
            
            // Si falla, devolvemos valores por defecto para que el Front no se rompa
            return {
                total_pacientes: 0,
                citas_hoy: 0,
                error: true
            };
        }
    }
};

export default dashboardService;