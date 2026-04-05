import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/api/pacientes/';

const registrarPaciente = async (formData) => {
    // 1. Intentamos obtener el token
    const token = localStorage.getItem('userToken'); 

    // 2. Validación de seguridad "Client-Side"
    // Evita enviar peticiones basura al servidor si no hay sesión
    if (!token) {
        throw new Error("Sesión expirada o inválida. Por favor, vuelva a ingresar.");
    }

    // 3. Petición formal a la API
    // RF-29: El backend usa este token para aplicar el aislamiento Multi-tenant
    const response = await axios.post(`${API_URL}registrar/`, formData, {
        headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    });
    
    return response.data;
};

const pacienteService = { registrarPaciente };

export default pacienteService;