// ==============================================================================
// [SPRINT 2 - RF-06/07/08] Service Layer: API Client para Citas y Lista de Espera
// [T030] Validación de colisiones se maneja en el backend
// [T031] Lista de espera con prioridades
// ==============================================================================
import apiClient from '../api/axiosConfig';

const citaService = {
    /**
     * RF-08: Obtener citas con filtros opcionales para calendario.
     * @param {Object} filtros - { fecha_inicio, fecha_fin, psicologo_id, estado }
     */
    getCitas: async (filtros = {}) => {
        const params = new URLSearchParams();
        if (filtros.fecha_inicio) params.append('fecha_inicio', filtros.fecha_inicio);
        if (filtros.fecha_fin) params.append('fecha_fin', filtros.fecha_fin);
        if (filtros.psicologo_id) params.append('psicologo_id', filtros.psicologo_id);
        if (filtros.estado) params.append('estado', filtros.estado);

        const response = await apiClient.get(`citas/?${params.toString()}`);
        return response.data;
    },

    /**
     * RF-06: Crear nueva cita con validación de colisiones.
     * El backend devuelve 400 si hay colisión de horario.
     */
    crearCita: async (data) => {
        const response = await apiClient.post('citas/', data);
        return response.data;
    },

    /**
     * RF-07: Actualizar cita existente (reprogramar).
     */
    actualizarCita: async (id, data) => {
        const response = await apiClient.patch(`citas/${id}/`, data);
        return response.data;
    },

    /**
     * RF-07 / CU13: Cancelar cita (soft-cancel → estado CANCELADA).
     */
    cancelarCita: async (id) => {
        const response = await apiClient.delete(`citas/${id}/`);
        return response.data;
    },

    /**
     * RF-07: Marcar cita como completada.
     */
    completarCita: async (id) => {
        const response = await apiClient.patch(`citas/${id}/`, { estado: 'COMPLETADA' });
        return response.data;
    },

    // ==============================================================
    // T031: Lista de Espera
    // ==============================================================
    getListaEspera: async () => {
        const response = await apiClient.get('lista-espera/');
        return response.data;
    },

    agregarEspera: async (data) => {
        const response = await apiClient.post('lista-espera/', data);
        return response.data;
    },

    eliminarEspera: async (id) => {
        const response = await apiClient.delete(`lista-espera/${id}/`);
        return response.data;
    },
};

export default citaService;
