import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import RegistroPaciente from './components/RegistroPaciente';
import RegistroClinica from './components/RegistroClinica';

// Mejora: Protección de rutas con validación de Roles (RNF-03)
const PrivateRoute = ({ children, allowedRoles }) => {
    const token = localStorage.getItem('userToken');
    const userRole = localStorage.getItem('userRole'); // Obtenido en authService

    if (!token) {
        return <Navigate to="/" />;
    }

    // Si la ruta requiere un rol específico y el usuario no lo tiene
    if (allowedRoles && !allowedRoles.includes(userRole)) {
        return <Navigate to="/dashboard" />; // Redirigir al home si no tiene permiso
    }

    return children;
};

function App() {
    return (
        <Router>
            <Routes>
                {/* Ruta Pública */}
                <Route path="/" element={<Login />} />
                
                {/* Dashboard: Accesible por cualquier usuario autenticado */}
                <Route 
                    path="/dashboard" 
                    element={
                        <PrivateRoute>
                            <Dashboard />
                        </PrivateRoute>
                    } 
                />

                {/* T014: Registro de Pacientes (Psicólogos y Admin) */}
                <Route 
                    path="/registro-paciente" 
                    element={
                        <PrivateRoute allowedRoles={['ADMIN', 'PSICOLOGO']}>
                            <RegistroPaciente />
                        </PrivateRoute>
                    } 
                />

                {/* RF-29: Registro de Clínicas (Solo Administradores/SuperAdmin) */}
                <Route 
                    path="/registro-clinica" 
                    element={
                        <PrivateRoute allowedRoles={['ADMIN']}>
                            <RegistroClinica />
                        </PrivateRoute>
                    } 
                />

                {/* Redirección por defecto si la ruta no existe */}
                <Route path="*" element={<Navigate to="/" />} />
            </Routes>
        </Router>
    );
}

export default App;