// ==============================================================================
// [SPRINT 2 - RF-25/26/27] Service Layer: API Client para Finanzas
// [T058] Saldo de pacientes | [T059] Pagos y comprobantes PDF
// ==============================================================================
import apiClient from '../api/axiosConfig';

const finanzaService = {
    /**
     * T058: Obtener saldo actual del paciente.
     */
    getSaldo: async (pacienteId) => {
        const response = await apiClient.get(`finanzas/saldo/${pacienteId}/`);
        return response.data;
    },

    /**
     * RF-26: Listar transacciones del tenant.
     */
    getTransacciones: async () => {
        const response = await apiClient.get('finanzas/transacciones/');
        return response.data;
    },

    /**
     * RF-25 / T059: Registrar una transacción (PAGO, DEUDA, AJUSTE).
     */
    registrarTransaccion: async (data) => {
        const response = await apiClient.post('finanzas/transacciones/', data);
        return response.data;
    },

    /**
     * T059: Descargar comprobante PDF como Blob.
     * Abre el PDF en una nueva pestaña del navegador.
     */
    descargarComprobante: async (transaccionId) => {
        const response = await apiClient.get(
            `finanzas/comprobante/${transaccionId}/pdf/`,
            { responseType: 'blob' }
        );
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        window.open(url, '_blank');
    },

    /**
     * RF-27: Generar reporte económico personalizado por rango de fechas.
     */
    generarReporte: async (fechaInicio, fechaFin, generarAudio = true) => {
        const response = await apiClient.post('reportes/personalizado/', {
            fecha_inicio: fechaInicio,
            fecha_fin: fechaFin,
            generar_audio: generarAudio,
        });
        return response.data;
    },
};

export default finanzaService;
